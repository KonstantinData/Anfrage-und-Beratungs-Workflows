from enum import Enum
from pydantic import BaseModel, Field, field_validator

# 1. Erlaubte Auswahlwerte einschrenken


class KitchenType(str, Enum):
    ZEILE = "zeile"
    L_FORM = "l_form"
    INSEL = "insel"

# 2. Die gemeinsame Basis


class InquiryBase(BaseModel):
    customer_name: str = Field(..., min_length=2,
                               max_length=100, description="Kundenname")
    postal_code: str = Field(..., min_length=5, max_length=5,
                             pattern=r"^[0-9]{5}$", description="5-stellige deutsche PLZ")
    kitchen_type: KitchenType = Field(...,
                                      description="Gewünschte Küchenbauform")
    budget: float = Field(..., gt=0, description="Geplantes Budget in Euro")

# 3. Schema für die Eingabe (Post)


class InquiryCreate(InquiryBase):
    pass


class InquiryReplace(InquiryBase):
    """Require all business fields when replacing an existing inquiry."""


class InquiryUpdate(BaseModel):
    """Allow omitted fields while rejecting explicit null values."""

    customer_name: str | None = Field(
        default=None, min_length=2, max_length=100, description="Kundenname"
    )
    postal_code: str | None = Field(
        default=None, min_length=5, max_length=5,
        pattern=r"^[0-9]{5}$", description="5-stellige deutsche PLZ"
    )
    kitchen_type: KitchenType | None = Field(
        default=None, description="Gewünschte Küchenbauform"
    )
    budget: float | None = Field(
        default=None, gt=0, description="Geplantes Budget in Euro"
    )

    @field_validator("customer_name", "postal_code", "kitchen_type", "budget", mode="before")
    @classmethod
    def reject_explicit_null(cls, value):
        """Defaults allow omission; supplied fields must contain a value."""
        if value is None:
            raise ValueError("Das Feld darf nicht null sein; zum Beibehalten weglassen.")
        return value

# 4. Schema für die Ausgabe (Response)


class InquiryResponse(InquiryBase):
    id: int
    status: str = "neu"

    class Config:
        from_attributes = True

# Architektur-Detail:
# Warum machen wir das so? Wenn jemand eine Anfrage per POST sendet,
# darf er sich seine id oder seinen Bearbeitungsstatus nicht selbst aussuchen!
# Die id wird serverseitig erzeugt.
