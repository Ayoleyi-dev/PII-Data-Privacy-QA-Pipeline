# Privacy and Handling Notes

This repository contains **synthetic PII-like data only**. It is intended to demonstrate privacy-aware data handling without publishing real personal information.

## Decisions used in the demo

- Direct identifiers are removed or masked before analytical use.
- Customer IDs are pseudonymized with HMAC-SHA256.
- Date of birth is reduced to an age band rather than copied downstream.
- QA logs identify the field and failed rule without echoing the invalid raw PII value.
- The pseudonymization key comes from an environment variable and is not stored in the repository.
- Generated working data is kept out of version control.
- `.env`, key files and a `data/private/` path are explicitly ignored.

## If this were real production data

Code-level transformations would only be part of the privacy controls. I would also expect:

- approved storage locations;
- least-privilege access controls;
- encryption in transit and at rest;
- retention and deletion requirements;
- audit logging;
- incident-response procedures;
- documented purpose and organization-specific privacy requirements.

This project is a portfolio demonstration and is not a certification of compliance with any specific privacy law or framework.
