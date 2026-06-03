from services.parsers.base_parser import BaseParser


class HDFCParser(BaseParser):
    def parse(self) -> list[dict]:
        transactions: list[dict] = []

        for line in self.raw_text.splitlines():
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 7:
                continue

            date, narration, _value_date, ref_no, withdrawal, deposit, balance = parts
            if date.lower() in {"date", ""}:
                continue

            debit = self.clean_amount(withdrawal) if withdrawal else None
            credit = self.clean_amount(deposit) if deposit else None
            amount_type = "debit" if debit is not None else "credit"

            transactions.append(
                {
                    "date": self.parse_date(date),
                    "narration": narration,
                    "debit": debit,
                    "credit": credit,
                    "balance": self.clean_amount(balance),
                    "ref_no": ref_no,
                    "transaction_type": amount_type,
                    "bank": "HDFC",
                }
            )

        return transactions
