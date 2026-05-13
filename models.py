from dataclasses import dataclass


@dataclass(slots=True)
class ProductOffer:
    source: str
    title: str
    price: float
    currency: str
    url: str
    condition: str
    seller: str
    availability: str
    checked_at: str
    confidence: float
    raw_text: str
