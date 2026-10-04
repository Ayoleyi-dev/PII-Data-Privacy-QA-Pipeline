from datetime import date

from src.privacy import age_band, mask_email, mask_phone, pseudonymize
from src.validate import quality_summary, validate_rows

KEY = "test-only-secret"


def ref_fn(customer_id: str) -> str:
    return pseudonymize(customer_id, KEY)[:12]


def test_pseudonymization_is_deterministic():
    assert pseudonymize("CUST-001", KEY) == pseudonymize("CUST-001", KEY)
    assert pseudonymize("CUST-001", KEY) != pseudonymize("CUST-002", KEY)


def test_masking():
    assert mask_email("amina@example.com") == "a***@example.com"
    assert mask_phone("+2348012345678") == "***5678"


def test_age_band_reduces_precision():
    assert age_band(
        "2000-01-01",
        as_of=date(2026, 1, 2),
    ) == "25-34"


def test_validator_does_not_log_raw_email():
    rows = [
        {
            "customer_id": "CUST-1",
            "full_name": "Test User",
            "email": "bad-email",
            "phone": "+2348012345678",
            "date_of_birth": "1990-01-01",
            "address": "1 Test Road",
            "region": "Lagos",
            "account_status": "active",
        }
    ]

    issues = validate_rows(rows, ref_fn)

    assert "bad-email" not in str(issues)
    assert any(issue["rule"] == "email_format" for issue in issues)


def test_duplicate_ids_are_flagged():
    base = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+2348012345678",
        "date_of_birth": "1990-01-01",
        "address": "1 Test Road",
        "region": "Lagos",
        "account_status": "active",
    }

    issues = validate_rows(
        [
            {"customer_id": "CUST-1", **base},
            {"customer_id": "CUST-1", **base},
        ],
        ref_fn,
    )

    assert any(
        issue["rule"] == "duplicate_customer_id" for issue in issues
    )


def test_summary_counts_rows_not_issues():
    issues = [
        {"row_number": 2},
        {"row_number": 2},
        {"row_number": 3},
    ]

    summary = quality_summary(5, issues)

    assert summary["rows_with_issues"] == 2
    assert summary["rows_passing_all_checks"] == 3
