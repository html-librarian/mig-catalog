import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)

    @validator("name", "description", "category")
    def validate_xss(cls, v):
        if v is None:
            return v
        # Проверяем на XSS паттерны
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"javascript:",
            r"<img[^>]*onerror = ",
            r"<img[^>]*onload = ",
            r"<svg[^>]*onload = ",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Обнаружен потенциально опасный контент")
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)


class ItemResponse(ItemBase):
    uuid: str = Field(..., description="UUID товара")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
