from typing import Optional
from fastapi import FastAPI, HTTPException, Path, Query, status

# Import unserer Verträge aus dem Schichten modell
from app.schemas import InquiryCreate, InquiryResponse

app = FastAPI(
    title="Anfrage- und Beratungs-Workflows API",
    description="Backend-Schnittstelle zur Erfassung und Abfrage von Beratungsanfragen",
    version="1.0.0"
)

# Unser Pseudo-Speicher (simulierte Datenbank)
db_inquiries: dict[int, dict] = {}
id_counter = 1

# Route 1: Erstellen einer Anfrage


@app.post(
    "/inquiries",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Anfragen"]
)
def create_inquiry(inquiry_in: InquiryCreate):
    """
    Nimmt eine valisierte Anfrage entgegen, vergibt eine ID und speichert sie.
    """
    global id_counter

    new_data = inquiry_in.model_dump()
    new_data["id"] = id_counter
    new_data["status"] = "neu"

    db_inquiries[id_counter] = new_data
    id_counter += 1

    return new_data

# ROUTE 2: Alle Anfragen abrufen (optional mit Filter)


@app.get(
    "/inquiries",
    response_model=list[InquiryResponse],
    tags=["Anfragen"]
)
def get_all_inquiries(
    postal_code: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=5,
        description="Filter nach PLZ oder PLZ-Präfix"
    )
):
    """
    Liefert alle Anfragen zurück. Unterstützt Filterung über Query-Parameter.
    """
    items = list(db_inquiries.values())
    if postal_code:
        return [i for i in items if i["postal_code"].startswith(postal_code)]
    return items


# ROUTE 3: Einzelne Anfrage über Pfadparameter
@app.get(
    "/inquiries/{inquiry_id}",
    response_model=InquiryResponse,
    tags=["Anfragen"]
)
def get_inquiry(
    inquiry_id: int = Path(..., gt=0, description="Eindeutige ID der Anfrage")
):
    """
    Liefert eine bestimmte Anfrage anhand ihrer ID.
    Wirft einen 404-Fehler, falls nicht vorhanden.
    """
    if inquiry_id not in db_inquiries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anfrage mit ID {inquiry_id} wurde nicht gefunden."
        )
    return db_inquiries[inquiry_id]
