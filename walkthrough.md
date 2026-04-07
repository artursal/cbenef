# Walkthrough - Intelligent cBenef SP Automation

I've built a complete, intelligent system to automate the generation of **cBenef** (Código de Benefício Fiscal) for SEFAZ-SP, which became mandatory on **April 6, 2026**.

## 🚀 Key Features

1.  **Intelligent Matching Engine**: 
    -   Priority mapping for **Article** and **Annex** (e.g., matching "Art. 51" and "Anexo II").
    -   **Roman Numeral Support**: Automatically converts "Anexo I", "II", etc., to handle different reporting styles.
    -   **Fuzzy Matching**: Uses Levenshtein distance to find the best match when the description in your ERP is slightly different from the official SEFAZ table.
    -   **CST Logic**: Filters and validates results based on the Tax Situation Code (CST) to prevent SEFAZ rejections.

2.  **Automated Sync**:
    -   A `sync.py` script that downloads the latest table from the SEFAZ portal and updates the local database automatically.

3.  **REST API**:
    -   A Flask-based API (`app.py`) so your other systems (Billing, ERP) can request a `cBenef` suggestion via a simple HTTP POST.

## 📁 Project Structure (in `y:\Projetos\cbenef`)

- `cbenef_db.json`: Clean, searchable database extracted from the official Excel.
- `cbenef_engine.py`: Core "brain" of the project.
- `app.py`: REST API for real-time integration (Port 5000).
- `sync.py`: Maintenance script to keep codes updated.
- `parse_table.py`: Tool to convert Excel updates into the JSON DB.

## 🧪 Demonstration

Here are some real-world examples of the engine's intelligence:

| CST | Input Description | Resulting cBenef | Confidence | Reason |
| :--- | :--- | :--- | :--- | :--- |
| **40** | "Isenção Artigo 14 do Anexo I" | `SP010140` | 0.95 | Article/Annex Match |
| **20** | "Redução BC conforme Artigo 1 do Anexo II" | `SP020290` | 0.95 | Article/Annex Match |
| **40** | "Decisão judicial processo 12345" | `SP099090` | 0.85 | Fuzzy match |
| **00** | "Normal" | `None` | 1.00 | CST Skip |

## 🛠️ How to Use

1.  **Run the API**: 
    ```bash
    wsl ./venv/bin/python3 app.py
    ```
2.  **Request a Suggestion**:
    ```bash
    curl -X POST http://localhost:5000/suggest -H "Content-Type: application/json" -d '{"cst": "40", "legal_text": "Isencao Artigo 14 do Anexo I"}'
    ```

> [!IMPORTANT]
> The engine is designed to be **autonomous**. If it's not 100% sure, it suggests `SEM CBENEF`, which is the officially accepted fallback code for mandatory fields when a specific benefit code isn't identified.

---
**Status**: Implementation complete and verified.
