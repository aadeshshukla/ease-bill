from abc import ABC, abstractmethod
from datetime import datetime


class BaseParser(ABC):
    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    @abstractmethod
    def parse(self) -> list[dict]:
        """Extract transactions from raw statement text."""

    def clean_amount(self, value: str) -> float:
        normalized = value.replace(",", "").replace(" ", "").replace("*", "").strip()
        return float(normalized or 0)

    def parse_date(self, value: str) -> str:
        for fmt in ("%d/%m/%y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {value}")
