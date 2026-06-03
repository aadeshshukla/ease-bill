# AGENTS.md — BankStatement to TallyPrime XML Converter
> This file is the **single source of truth** for any AI agent (GitHub Copilot, Claude, GPT)
> working on this codebase. Read this fully before generating any code, file, or suggestion.

---

## 1. What We Are Building

A **full-stack web application** that:
1. Accepts PDF bank statements (uploaded by user)
2. Extracts and parses transaction data from them
3. Converts that data into **TallyPrime-compatible XML voucher import files**
4. Lets the user download the XML and import it directly into TallyPrime

**Target users:** Indian accountants (CAs), bookkeepers, and SME owners who use TallyPrime
and are tired of manually entering bank transactions.

**Core value:** Zero manual data entry. Upload PDF → Download Tally XML. Done.

---

## 2. Product Name

**StatementBridge** *(working title, can change)*

---

## 3. Tech Stack

### Backend
| Layer | Technology | Notes |
|-------|-----------|-------|
| Runtime | Python 3.11+ | |
| Framework | FastAPI | Async, OpenAPI docs auto-generated |
| PDF Text Extraction | pdfplumber | For digital/text-based PDFs |
| OCR | PaddleOCR | For scanned/image-based PDFs |
| XML Generation | lxml | For Tally XML output |
| Task Queue | None (Phase 1) / Celery (Phase 2) | |
| Database | SQLite (Phase 1) → PostgreSQL (Phase 2) | |
| ORM | SQLAlchemy | |
| Auth | JWT (python-jose) | |
| File Storage | Local filesystem (Phase 1) → S3 (Phase 2) | |

### Frontend
| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | React 18 | Vite-based setup |
| Styling | Tailwind CSS | |
| HTTP Client | Axios | |
| File Upload | react-dropzone | Drag-and-drop UX |
| State | useState / useContext | No Redux needed in Phase 1 |
| Routing | React Router v6 | |

### Dev & Infra
| Tool | Purpose |
|------|---------|
| Docker + docker-compose | Local dev environment |
| GitHub Actions | CI/CD |
| Vercel | Frontend deployment |
| Railway / Render | Backend deployment |
| pytest | Backend testing |
| Vitest | Frontend testing |

---

## 4. Project Folder Structure

```
ease-bill/
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── config.py                # Env vars, settings
│   ├── database.py              # SQLAlchemy setup
│   ├── models/
│   │   ├── user.py
│   │   └── upload.py
│   ├── routers/
│   │   ├── auth.py              # /auth/register, /auth/login
│   │   ├── upload.py            # /upload/pdf
│   │   └── export.py            # /export/xml
│   ├── services/
│   │   ├── pdf_extractor.py     # pdfplumber text extraction
│   │   ├── ocr_engine.py        # PaddleOCR for scanned PDFs
│   │   ├── bank_detector.py     # Detects which bank the PDF is from
│   │   ├── parsers/
│   │   │   ├── base_parser.py   # Abstract base class for all parsers
│   │   │   ├── hdfc_parser.py
│   │   │   ├── sbi_parser.py
│   │   │   ├── icici_parser.py
│   │   │   ├── axis_parser.py
│   │   │   ├── kotak_parser.py
│   │   │   ├── pnb_parser.py
│   │   │   ├── bob_parser.py
│   │   │   └── generic_llm_parser.py  # Fallback: Claude/GPT parses unknown formats
│   │   └── tally_xml_generator.py     # Converts transactions → Tally XML
│   ├── schemas/
│   │   ├── transaction.py       # Pydantic model for a transaction
│   │   └── export.py            # Pydantic model for XML export request
│   └── tests/
│       ├── test_parsers/
│       └── test_xml_generator.py
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx         # Landing page
│   │   │   ├── Upload.jsx       # PDF upload + processing
│   │   │   ├── Preview.jsx      # Review parsed transactions
│   │   │   └── Dashboard.jsx    # Upload history
│   │   ├── components/
│   │   │   ├── Dropzone.jsx
│   │   │   ├── TransactionTable.jsx
│   │   │   ├── DownloadButton.jsx
│   │   │   └── Navbar.jsx
│   │   └── api/
│   │       └── client.js        # Axios instance + API calls
│
├── docker-compose.yml
├── .env.example
├── AGENTS.md                    # ← You are here
└── README.md
```

---

## 5. Core Data Models

### Transaction (Pydantic / Python)
```python
class Transaction(BaseModel):
    date: str              # Format: DD-MM-YYYY
    narration: str         # Transaction description
    debit: Optional[float] # Amount debited (None if credit)
    credit: Optional[float]# Amount credited (None if debit)
    balance: Optional[float]
    ref_no: Optional[str]  # Cheque no / UTR / reference
    transaction_type: str  # "debit" | "credit"
    bank: str              # e.g. "HDFC", "SBI"
```

### Upload Record (SQLAlchemy)
```python
class Upload(Base):
    id: int
    user_id: int
    filename: str
    bank_detected: str
    total_transactions: int
    status: str            # "processing" | "done" | "failed"
    created_at: datetime
    xml_path: str          # path to generated XML file
```

---

## 6. Processing Pipeline (Step by Step)

```
[User uploads PDF]
        ↓
[Step 1] pdf_extractor.py
  → Try pdfplumber first (text-based PDF)
  → If text extraction fails or is empty → fall back to ocr_engine.py (PaddleOCR)
        ↓
[Step 2] bank_detector.py
  → Scan extracted text for keywords:
    - "HDFC BANK", "HDFC Ltd" → HDFC
    - "State Bank of India", "SBI" → SBI
    - "ICICI BANK" → ICICI
    - "AXIS BANK" → Axis
    - "KOTAK MAHINDRA" → Kotak
    - "Punjab National Bank", "PNB" → PNB
    - "Bank of Baroda", "BOB" → BOB
  → If unknown → route to generic_llm_parser.py
        ↓
[Step 3] parsers/<bank>_parser.py
  → Each parser extends base_parser.py
  → Returns List[Transaction]
        ↓
[Step 4] tally_xml_generator.py
  → Takes List[Transaction]
  → Returns TallyPrime-compatible XML string
        ↓
[Step 5] Save XML to disk, return download URL to frontend
```

---

## 7. Tally XML Format Reference

TallyPrime accepts voucher imports in this exact XML structure.
**Do not deviate from this format.**

```xml
<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>##SVCURRENTCOMPANY</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>

        <!-- One TALLYMESSAGE per transaction -->
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="Receipt" ACTION="Create">
            <DATE>20260603</DATE>                   <!-- YYYYMMDD format -->
            <NARRATION>UPI/123456/PAYMENT</NARRATION>
            <VOUCHERTYPENAME>Receipt</VOUCHERTYPENAME>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Bank Account</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <AMOUNT>-5000.00</AMOUNT>             <!-- Negative for debit side -->
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Suspense Account</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>5000.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>

      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
```

**Rules:**
- Voucher type is `Receipt` for credits, `Payment` for debits
- Date must be `YYYYMMDD` (no separators)
- Amount for bank ledger entry is always **negative**
- Suspense Account is the default counterpart ledger until user maps it
- `ISDEEMEDPOSITIVE` is `Yes` for the bank side, `No` for the counterpart

---

## 8. Bank Parser Implementation Guide

Each bank parser must follow this contract:

```python
# backend/services/parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import List
from schemas.transaction import Transaction

class BaseParser(ABC):
    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    @abstractmethod
    def parse(self) -> List[Transaction]:
        """Extract transactions from raw_text. Must return List[Transaction]."""
        pass

    def clean_amount(self, value: str) -> float:
        """Remove commas, spaces, convert to float."""
        return float(value.replace(",", "").replace(" ", "").strip() or 0)

    def parse_date(self, value: str) -> str:
        """Normalize date to DD-MM-YYYY regardless of source format."""
        pass
```

### Bank-Specific Notes for Parsers

| Bank | Statement Format Notes |
|------|----------------------|
| **HDFC** | Table with columns: Date \| Narration \| Value Dt \| Ref No./Cheque No. \| Withdrawal Amt \| Deposit Amt \| Closing Balance. Date format: `DD/MM/YY` |
| **SBI** | Columns: Txn Date \| Value Date \| Description \| Ref No./Cheque No \| Debit \| Credit \| Balance. Date format: `DD MMM YYYY` |
| **ICICI** | Columns: S No. \| Transaction Date \| Value Date \| Description \| Ref No. \| Debit \| Credit \| Balance. Date format: `DD/MM/YYYY` |
| **Axis** | Columns: Tran Date \| Chq./Ref.No. \| Particulars \| Debit \| Credit \| Balance. Date format: `DD-MM-YYYY` |
| **Kotak** | Columns: Transaction Date \| Description \| Chq/Ref Number \| Branch Code \| Debit \| Credit \| Balance. Date: `DD-MM-YYYY` |
| **PNB** | Columns: Date \| Particulars \| Cheque No \| Debit \| Credit \| Balance. Date: `DD/MM/YYYY`. Often has multi-line narrations. |
| **BoB** | Similar to SBI layout. Date: `DD/MM/YYYY`. May have asterisks in amount fields. |

---

## 9. API Endpoints Reference

```
POST   /auth/register          Body: {email, password, name}
POST   /auth/login             Body: {email, password} → returns JWT

POST   /upload/pdf             Body: multipart/form-data (file) → returns upload_id + parsed transactions
GET    /upload/history         Returns list of past uploads for logged-in user

POST   /export/xml             Body: {upload_id, company_name, bank_ledger_name} → returns XML download URL
GET    /export/download/{id}   Streams the XML file

GET    /health                 Health check
```

---

## 10. Frontend Pages & Flow

```
/ (Home)
  → Marketing landing page
  → CTA: "Upload Bank Statement"

/upload
  → Drag-and-drop PDF upload
  → Shows upload progress
  → On success: redirects to /preview/:upload_id

/preview/:upload_id
  → Shows parsed transactions in a table
  → User can edit/delete individual rows
  → Input fields: Company Name, Bank Ledger Name (for XML)
  → Button: "Generate Tally XML"
  → On success: shows download button

/dashboard
  → Table of past uploads
  → Re-download XML for any previous upload
```

---

## 11. Environment Variables

```env
# backend/.env
DATABASE_URL=sqlite:///./statementbridge.db
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Optional: LLM fallback for unknown bank formats
ANTHROPIC_API_KEY=sk-ant-...
LLM_FALLBACK_ENABLED=true
```

---

## 12. Development Phases

### Phase 1 — Core MVP
- [ ] FastAPI backend scaffold
- [ ] PDF upload endpoint
- [ ] pdfplumber text extraction
- [ ] HDFC parser (first bank)
- [ ] Tally XML generator
- [ ] React frontend: upload + preview + download
- [ ] SQLite database
- [ ] Basic JWT auth

### Phase 2 — Parser Expansion
- [ ] SBI parser
- [ ] ICICI parser
- [ ] Axis parser
- [ ] Kotak parser
- [ ] PaddleOCR integration for scanned PDFs
- [ ] LLM fallback parser (Claude API) for unknown banks

### Phase 3 — Product Features
- [ ] PNB, BoB parsers
- [ ] User dashboard with upload history
- [ ] GST ledger tagging suggestions
- [ ] Duplicate transaction detection
- [ ] Razorpay payment integration
- [ ] Free tier limits (5 uploads/day)
- [ ] PostgreSQL migration
- [ ] Docker production setup

---

## 13. Key Rules for AI Code Generation

> GitHub Copilot and other agents MUST follow these rules at all times:

1. **Never hardcode bank names as strings** outside of `bank_detector.py`. Use constants.
2. **Every parser must extend `BaseParser`** — never write a standalone parser function.
3. **All dates in internal processing use `DD-MM-YYYY`**. Tally XML uses `YYYYMMDD`. Conversion happens only in `tally_xml_generator.py`.
4. **Never put business logic in routers**. Routers call services. Services do the work.
5. **All amounts are stored as `float`**, never `str`.
6. **The XML generator must never raise an exception silently** — always propagate errors up.
7. **Frontend never calls the backend directly from components** — all API calls go through `src/api/client.js`.
8. **Use Pydantic schemas for all request/response validation** — no raw dicts in endpoints.
9. **Write a test for every new parser** under `backend/tests/test_parsers/`.
10. **Comments in code must explain WHY, not WHAT** — the code explains what.

---

## 14. Sample Transaction Output (after parsing)

```json
[
  {
    "date": "01-06-2026",
    "narration": "UPI/234567891011/Payment to Swiggy",
    "debit": 450.00,
    "credit": null,
    "balance": 12340.50,
    "ref_no": "234567891011",
    "transaction_type": "debit",
    "bank": "HDFC"
  },
  {
    "date": "02-06-2026",
    "narration": "NEFT CR/AXIS123456/Salary June",
    "debit": null,
    "credit": 55000.00,
    "balance": 67340.50,
    "ref_no": "AXIS123456",
    "transaction_type": "credit",
    "bank": "HDFC"
  }
]
```

---

## 15. Out of Scope (Do Not Build Unless Instructed)

- Direct Tally API/TCP integration (future phase)
- Mobile app
- Multi-currency support
- Support for non-Indian banks
- Automated accounting (ledger assignment AI) — Phase 3 only
- Browser extension

---

*Last updated: June 2026 | Maintainer: Aadesh Shukla (Mausam)*