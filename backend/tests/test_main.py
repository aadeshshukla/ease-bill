from fastapi.testclient import TestClient

from main import app
from routers import auth
from services.parsers.hdfc_parser import HDFCParser
from services.pdf_extractor import PDFExtractor
from services.tally_xml_generator import generate_tally_xml

client = TestClient(app)


def setup_function() -> None:
    auth._USERS.clear()


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_includes_cors_headers_for_frontend_origin() -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_register_success() -> None:
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123", "name": "User"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


def test_login_success() -> None:
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123", "name": "User"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials() -> None:
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_upload_pdf_success() -> None:
    response = client.post(
        "/upload/pdf",
        files={"file": ("statement.pdf", b"pdf-bytes", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"


def test_upload_pdf_invalid_extension() -> None:
    response = client.post(
        "/upload/pdf",
        files={"file": ("notes.txt", b"plain-text", "text/plain")},
    )
    assert response.status_code == 400


def test_pdf_extractor_initialization_defaults() -> None:
    extractor = PDFExtractor()
    assert extractor.ocr_enabled is False


def test_pdf_extractor_initialization_with_ocr() -> None:
    extractor = PDFExtractor(ocr_enabled=True)
    assert extractor.ocr_enabled is True


def test_hdfc_parser_parses_transaction() -> None:
    raw_text = (
        "Date|Narration|Value Dt|Ref No./Cheque No.|Withdrawal Amt|Deposit Amt|Closing "
        "Balance\n01/06/24|UPI PAYMENT|01/06/24|123456|500.00||1000.00"
    )
    transactions = HDFCParser(raw_text).parse()
    assert len(transactions) == 1
    assert transactions[0]["bank"] == "HDFC"
    assert transactions[0]["transaction_type"] == "debit"


def test_hdfc_amount_parsing_handles_commas() -> None:
    parser = HDFCParser("")
    assert parser.clean_amount("1,23,456.78") == 123456.78


def test_hdfc_date_parsing() -> None:
    parser = HDFCParser("")
    assert parser.parse_date("01/06/24") == "01-06-2024"


def test_tally_xml_generator_for_debit() -> None:
    xml = generate_tally_xml(
        [
            {
                "date": "01-06-2024",
                "narration": "UPI PAYMENT",
                "debit": 500.0,
                "credit": None,
                "transaction_type": "debit",
            }
        ]
    )
    assert '<VOUCHER VCHTYPE="Payment" ACTION="Create">' in xml
    assert "<DATE>20240601</DATE>" in xml
    assert "<AMOUNT>-500.00</AMOUNT>" in xml


def test_tally_xml_generator_for_credit() -> None:
    xml = generate_tally_xml(
        [
            {
                "date": "02-06-2024",
                "narration": "SALARY",
                "debit": None,
                "credit": 1000.0,
                "transaction_type": "credit",
            }
        ]
    )
    assert '<VOUCHER VCHTYPE="Receipt" ACTION="Create">' in xml
    assert "<AMOUNT>1000.00</AMOUNT>" in xml
