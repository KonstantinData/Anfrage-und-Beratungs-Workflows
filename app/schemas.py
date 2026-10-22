from enum import Enum
from pydantic import BaseModel, Field

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
