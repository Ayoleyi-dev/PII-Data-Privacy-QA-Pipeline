"""Quality checks for synthetic customer data containing PII-like fields."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+234\d{10}$")


def _issue(
    row_number: int,
    customer_ref: str,
    field: str,
    rule: str,
    severity: str,
    message: str,
) -> dict[str, Any]:
    # Raw PII values are intentionally excluded from the QA log.
    return {
        "row_number": row_number,
        "customer_ref": customer_ref,
        "field": field,
        "rule": rule,
        "severity": severity,
        "message": message,
    }


def validate_rows(
    rows: list[dict[str, str]],
    customer_ref_fn,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}

    for row_number, row in enumerate(rows, start=2):
        customer_id = row.get("customer_id", "").strip()
        customer_ref = (
            customer_ref_fn(customer_id) if customer_id else "MISSING_ID"
        )

        for field in [
            "customer_id",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
        ]:
            if not row.get(field, "").strip():
                issues.append(
                    _issue(
                        row_number,
                        customer_ref,
                        field,
                        "required_field",
                        "ERROR",
                        f"Required field '{field}' is missing.",
                    )
                )

        if customer_id:
            if customer_id in seen_ids:
                issues.append(
                    _issue(
                        row_number,
                        customer_ref,
                        "customer_id",
                        "duplicate_customer_id",
                        "CRITICAL",
                        (
                            "Duplicate customer_id; first seen on "
                            f"row {seen_ids[customer_id]}."
                        ),
                    )
                )
            else:
                seen_ids[customer_id] = row_number

        email = row.get("email", "").strip()
        if email and not EMAIL_RE.fullmatch(email):
            issues.append(
                _issue(
                    row_number,
                    customer_ref,
                    "email",
                    "email_format",
                    "ERROR",
                    "Email format is invalid.",
                )
            )

        phone = row.get("phone", "").strip()
        if phone and not PHONE_RE.fullmatch(phone):
            issues.append(
                _issue(
                    row_number,
                    customer_ref,
                    "phone",
                    "phone_format",
                    "ERROR",
                    "Phone must use +234 followed by 10 digits.",
                )
            )

        dob_text = row.get("date_of_birth", "").strip()
        if dob_text:
            try:
                dob = datetime.strptime(dob_text, "%Y-%m-%d").date()
                if dob > date.today():
                    issues.append(
                        _issue(
                            row_number,
                            customer_ref,
                            "date_of_birth",
                            "future_date",
                            "ERROR",
                            "Date of birth cannot be in the future.",
                        )
                    )
            except ValueError:
                issues.append(
                    _issue(
                        row_number,
                        customer_ref,
                        "date_of_birth",
                        "date_format",
                        "ERROR",
                        "Date of birth must use YYYY-MM-DD.",
                    )
                )

        if row.get("account_status", "").strip() not in {
            "active",
            "inactive",
        }:
            issues.append(
                _issue(
                    row_number,
                    customer_ref,
                    "account_status",
                    "allowed_values",
                    "WARNING",
                    "Account status should be active or inactive.",
                )
            )

    return issues


def quality_summary(
    total_rows: int,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    affected_rows = {issue["row_number"] for issue in issues}
    passing = total_rows - len(affected_rows)

    return {
        "total_rows": total_rows,
        "rows_with_issues": len(affected_rows),
        "rows_passing_all_checks": passing,
        "pass_rate_pct": round((passing / total_rows * 100), 2)
        if total_rows
        else 0.0,
        "total_issues": len(issues),
    }
