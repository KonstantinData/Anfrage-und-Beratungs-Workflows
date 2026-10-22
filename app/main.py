from typing import Optional
from fastapi import FastAPI, HTTPException, Path, Query, Response, status

# Import unserer Verträge aus dem Schichten modell
from app.schemas import InquiryCreate, InquiryReplace, InquiryResponse, InquiryUpdate

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


@app.put(
    "/inquiries/{inquiry_id}",
    response_model=InquiryResponse,
    tags=["Anfragen"]
)
def replace_inquiry(
    inquiry_in: InquiryReplace,
    inquiry_id: int = Path(..., gt=0, description="Eindeutige ID der Anfrage")
):
    """Replace all business fields while preserving server-managed fields."""
    existing = get_inquiry(inquiry_id)
    replacement = inquiry_in.model_dump()
    replacement["id"] = existing["id"]
    replacement["status"] = existing["status"]
    db_inquiries[inquiry_id] = replacement
    return replacement


@app.patch(
    "/inquiries/{inquiry_id}",
    response_model=InquiryResponse,
    tags=["Anfragen"]
)
def update_inquiry(
    inquiry_in: InquiryUpdate,
    inquiry_id: int = Path(..., gt=0, description="Eindeutige ID der Anfrage")
):
    """Update only explicitly supplied business fields."""
    existing = get_inquiry(inquiry_id)
    changes = inquiry_in.model_dump(exclude_unset=True)
    existing.update(changes)
    return existing


@app.delete(
    "/inquiries/{inquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["Anfragen"]
)
def delete_inquiry(
    inquiry_id: int = Path(..., gt=0, description="Eindeutige ID der Anfrage")
) -> Response:
    """Delete an existing inquiry and return an empty response."""
    get_inquiry(inquiry_id)
    del db_inquiries[inquiry_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
