# Intelligent and Automated cBenef SP Generator

This project aims to automate the generation of the `cBenef` field (Código de Benefício Fiscal) for SEFAZ-SP, which became mandatory on **April 6, 2026**.

## Proposed Strategy

1.  **Data Preparation**:
    -   **Automated Download**: A script to pull the latest official `cBenef` Excel table from the SEFAZ portal.
    -   **JSON Conversion**: Parsing the Excel file using Python (pandas) to create a structured, searchable JSON database.

2.  **Lookup Engine**:
    -   **Attribute Matching**: Matching `cBenef` based on:
        -   **CST**: Tax Situation (20, 30, 40, 41, 50, 51, 70, etc.)
        -   **Legal Basis**: Matching keywords like "Anexo I Art. 51" or "Isenção".
        -   **NCM**: Handling products with specific benefit rules based on NCM.
    -   **Verification**: Ensuring the `cBenef` is valid for the given CST (to avoid SEFAZ rejection).

3.  **Automation Components**:
    -   `sync.py`: Periodically checks and updates the codes.
    -   `cbenef_engine.py`: A library or CLI for real-time querying.

## User Review Required

> [!IMPORTANT]
> The effectiveness of the "intelligent" part (matching descriptions and legal basis) depends on having a standardized input format for your product benefits. The tool will suggest the best match but can also be configured with a manual override map for specific NCMs.

## Open Questions

- Does your current ERP/Software use a specific format for the "Legal Provision" (Dispositivo Legal) field?
- Should the tool be a standalone CLI or integrated as a library into your project?

## Verification Plan

### Automated Tests
- Test cases mapping realistic CST/NCM combinations to expected cBenef codes.
- Batch validation of common tax benefit scenarios.

### Manual Verification
- Visual inspection of the parsed JSON database (comparing with the Excel file).
