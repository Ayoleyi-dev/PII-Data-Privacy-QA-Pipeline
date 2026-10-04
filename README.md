# PII Data Privacy & Quality Assurance Pipeline

![Tests](https://github.com/Ayoleyi-dev/PII-Data-Privacy-QA-Pipeline/actions/workflows/tests.yml/badge.svg)

A small Python project showing how I would validate customer data that contains personally identifiable information (PII) while keeping downstream analytical outputs privacy-safe.

> **No real personal data is included in this repository.** The names, emails, phone numbers, dates of birth and addresses in the sample dataset are synthetic and exist only to demonstrate the workflow.

## Why I built this

Data quality and privacy often overlap. A dataset can be accurate but handled carelessly, or privacy-safe but still contain duplicates, missing values and invalid records.

This project combines both responsibilities:

1. **Quality assurance** — checking records for completeness, uniqueness, format validity and impossible values.
2. **Privacy-aware handling** — reducing or removing identifying information before the data is used for analysis.

## Workflow

```text
Synthetic customer data
        |
        v
PII field review
        |
        v
Data-quality checks
        |
        +------> privacy-safe QA issues
        |
        v
De-identification
        |
        +------> pseudonymized customer ID
        +------> masked email / phone
        +------> DOB reduced to age band
        +------> name / street address removed
        |
        v
De-identified analytical dataset
```

## PII handling decisions

| Field | Classification | Analytical handling |
|---|---|---|
| Customer ID | Operational identifier | Pseudonymized with HMAC-SHA256 |
| Full name | Direct identifier | Removed |
| Email | Direct identifier | Masked |
| Phone | Direct identifier | Masked |
| Date of birth | Quasi-identifier | Reduced to an age band |
| Street address | Direct identifier | Removed |
| Region | Quasi-identifier | Retained for aggregate analysis |
| Account status | Operational field | Retained |

The pseudonymization key is read from the `PII_HASH_KEY` environment variable rather than stored in the source code.

The full field inventory is in [`docs/pii_inventory.json`](docs/pii_inventory.json).

## Quality checks

The QA layer checks for:

- missing required fields;
- duplicate customer IDs;
- invalid email format;
- invalid Nigerian phone-number format;
- invalid date format;
- future dates of birth;
- unexpected account-status values.

The QA report deliberately records the **field and rule that failed without copying the raw bad PII value into the log**.

## Demo results

The included synthetic dataset contains 16 rows, with several errors deliberately added for testing.

| Metric | Result |
|---|---:|
| Rows processed | 16 |
| Rows passing all checks | 10 |
| Rows with issues | 6 |
| Total issues | 6 |
| Pass rate | 62.5% |

A privacy-safe example summary and issue log are available in the [`examples/`](examples/) folder.

## Project structure

```text
.
├── data/
│   ├── README.md
│   └── raw/
│       └── synthetic_customers.csv
├── docs/
│   ├── pii_inventory.json
│   └── privacy_notes.md
├── examples/
│   ├── qa_issues_sample.csv
│   └── qa_summary.json
├── src/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── privacy.py
│   └── validate.py
├── tests/
│   └── test_privacy_pipeline.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Run the project

Install the development dependency:

```bash
pip install -r requirements.txt
```

Set a demo hashing key.

**macOS / Linux**

```bash
export PII_HASH_KEY="replace-with-a-demo-key"
```

**Windows PowerShell**

```powershell
$env:PII_HASH_KEY="replace-with-a-demo-key"
```

Run the pipeline:

```bash
python -m src.pipeline
```

Run the tests:

```bash
python -m pytest -q
```

The generated files are written under `data/processed/` and are intentionally ignored by Git.

## Outputs

The pipeline generates:

- **`deidentified_customers.csv`** — analytical data with direct identifiers removed or masked;
- **`qa_issues.csv`** — privacy-safe validation issues;
- **`qa_summary.json`** — overall QA metrics.

## Tests

The automated tests currently cover:

- deterministic pseudonymization;
- email and phone masking;
- DOB reduction to age bands;
- prevention of raw invalid email values appearing in QA logs;
- duplicate-ID detection;
- correct row-level QA summary counts.

GitHub Actions runs the test suite automatically on pushes and pull requests.

## Privacy notes

This project demonstrates good handling patterns; it is **not a claim of regulatory compliance**.

For real production PII, the code would be only one part of the control environment. I would also expect approved storage, least-privilege access, encryption in transit and at rest, retention/deletion rules, audit logging, incident procedures, and organization-specific privacy requirements.

See [`docs/privacy_notes.md`](docs/privacy_notes.md) for the project-specific handling assumptions.

## What this project demonstrates

The focus is the practical review step before sensitive customer data is used downstream: identify what is sensitive, validate the records, avoid leaking PII into logs, and reduce the dataset to only the information needed for analysis.

The repository uses synthetic PII so those practices can be demonstrated publicly without exposing real customer information.
