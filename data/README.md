# Data

The repository sample is **fully synthetic** and contains no real customer data.

`raw/synthetic_customers.csv` includes deliberately introduced QA problems so the validator has something meaningful to detect:

- one malformed email;
- one malformed phone number;
- one missing date of birth;
- one missing full name;
- one future date of birth;
- one duplicate customer ID.

The `processed/` directory is generated locally and ignored by Git. The repository includes privacy-safe examples under `examples/` instead of committing generated working files.

The names, addresses and contact details in the sample are fictitious and should not be treated as real customer information.
