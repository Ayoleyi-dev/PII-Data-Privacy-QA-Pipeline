"""Privacy-safe transformations for synthetic customer data."""
from __future__ import annotations

import hashlib
import hmac
import os
import re
from datetime import date, datetime
from typing import Any


def require_hash_key() -> str:
    key = os.getenv("PII_HASH_KEY")
    if not key:
        raise RuntimeError(
            "PII_HASH_KEY is required. Use a non-production demo key for this synthetic dataset."
        )
    return key


def pseudonymize(value: str, key: str) -> str:
    """Create a deterministic keyed pseudonym for an identifier."""
    digest = hmac.new(
        key.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:20]


def mask_email(email: str) -> str:
    """Keep only the first local-part character and the domain."""
    if not isinstance(email, str) or "@" not in email:
        return ""
    local, domain = email.split("@", 1)
    if not local or not domain:
        return ""
    return f"{local[0]}***@{domain}"


def mask_phone(phone: str) -> str:
    """Keep only the final four digits of a phone number."""
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) < 4:
        return ""
    return f"***{digits[-4:]}"


def age_band(date_of_birth: str, as_of: date | None = None) -> str:
    """Reduce date-of-birth precision to an age band."""
    if not date_of_birth:
        return "Unknown"

    as_of = as_of or date.today()

    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        return "Unknown"

    if dob > as_of:
        return "Unknown"

    age = as_of.year - dob.year - (
        (as_of.month, as_of.day) < (dob.month, dob.day)
    )

    if age < 18:
        return "<18"
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    if age < 65:
        return "55-64"
    return "65+"


def deidentify_record(row: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a minimized analytical record without direct identifiers."""
    customer_id = str(row.get("customer_id", "")).strip()

    return {
        "customer_key": pseudonymize(customer_id, key) if customer_id else "",
        "email_masked": mask_email(str(row.get("email", ""))),
        "phone_masked": mask_phone(str(row.get("phone", ""))),
        "age_band": age_band(str(row.get("date_of_birth", ""))),
        "region": str(row.get("region", "")).strip(),
        "account_status": str(row.get("account_status", "")).strip(),
    }
