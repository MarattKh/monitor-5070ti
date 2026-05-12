from pydantic import BaseModel, HttpUrl


class ProductOffer(BaseModel):
    source: str
    title: str
    price: float | None
    in_stock: bool
    url: HttpUrl
