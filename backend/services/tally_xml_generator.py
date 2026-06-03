from xml.etree.ElementTree import Element, SubElement, tostring


def _to_tally_date(date_value: str) -> str:
    day, month, year = date_value.split("-")
    return f"{year}{month}{day}"


def generate_tally_xml(
    transactions: list[dict], bank_ledger_name: str = "Bank Account"
) -> str:
    envelope = Element("ENVELOPE")
    header = SubElement(envelope, "HEADER")
    SubElement(header, "TALLYREQUEST").text = "Import Data"

    body = SubElement(envelope, "BODY")
    import_data = SubElement(body, "IMPORTDATA")
    request_desc = SubElement(import_data, "REQUESTDESC")
    SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    request_data = SubElement(import_data, "REQUESTDATA")

    for txn in transactions:
        message = SubElement(request_data, "TALLYMESSAGE", {"xmlns:UDF": "TallyUDF"})
        voucher_type = (
            "Payment" if txn.get("transaction_type") == "debit" else "Receipt"
        )
        voucher = SubElement(
            message, "VOUCHER", {"VCHTYPE": voucher_type, "ACTION": "Create"}
        )

        amount = txn.get("debit") if txn.get("debit") is not None else txn.get("credit")
        amount_value = float(amount or 0)

        SubElement(voucher, "DATE").text = _to_tally_date(txn["date"])
        SubElement(voucher, "NARRATION").text = txn.get("narration", "")
        SubElement(voucher, "VOUCHERTYPENAME").text = voucher_type

        bank_entry = SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        SubElement(bank_entry, "LEDGERNAME").text = bank_ledger_name
        SubElement(bank_entry, "ISDEEMEDPOSITIVE").text = "Yes"
        SubElement(bank_entry, "AMOUNT").text = f"-{amount_value:.2f}"

        counter_entry = SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        SubElement(counter_entry, "LEDGERNAME").text = "Suspense Account"
        SubElement(counter_entry, "ISDEEMEDPOSITIVE").text = "No"
        SubElement(counter_entry, "AMOUNT").text = f"{amount_value:.2f}"

    return tostring(envelope, encoding="unicode")
