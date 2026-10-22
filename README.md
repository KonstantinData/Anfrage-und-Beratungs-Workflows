# Anfrage- und Beratungs-Workflows

**Python-Backend zur strukturierten Erfassung und Abfrage von Küchenberatungsanfragen.**

Dieses Portfolio-Projekt zeigt, wie sich ein fachlicher Anwendungsfall in eine typisierte REST-API übersetzen lässt: Eine Anfrage enthält Kundenname, Postleitzahl, gewünschte Küchenform und Budget. Die API prüft die Eingaben, vergibt eine ID und macht die Anfrage für weitere Abfragen verfügbar.

Der Fokus liegt auf einem überschaubaren, nachvollziehbaren Backend mit klaren Datenmodellen, definierten HTTP-Antworten und interaktiver API-Dokumentation.

## Auf einen Blick

| Aspekt | Umsetzung |
| --- | --- |
| Anwendungsfall | Beratungsanfragen im Küchenumfeld erfassen und abrufen |
| Sprache | Python |
| Frameworks | FastAPI, Pydantic |
| Server | Uvicorn |
| Schnittstelle | REST mit JSON und automatisch erzeugtem OpenAPI-Schema |
| Speicherung | Prozesslokaler In-Memory-Speicher |
| Stand | Lokal ausführbarer Backend-Prototyp |

## Welche Fähigkeiten das Projekt zeigt

| Kompetenz | Konkreter Nachweis im Code |
| --- | --- |
| Fachliche Anforderungen modellieren | Kundenname, PLZ, Küchenform und Budget werden in einem gemeinsamen Basismodell beschrieben. |
| REST-Schnittstellen entwickeln | POST, GET, PUT, PATCH und DELETE bilden Anlegen, Lesen, Ersetzen, Teiländerungen und Löschen ab. |
| Eingaben validieren | Pydantic prüft Zeichenlängen, das PLZ-Format, erlaubte Küchenformen und ein positives Budget. |
| Eingabe und Ausgabe trennen | Eigene Modelle beschreiben Anlegen, vollständiges Ersetzen und Teiländerungen; `InquiryResponse` ergänzt die Serverfelder `id` und `status`. |
| Fehlerfälle behandeln | Ungültige Eingaben führen zu HTTP `422`, unbekannte Anfragen zu HTTP `404`. |
| Code strukturieren | Datenmodelle liegen in `app/schemas.py`, Endpunkte und Anwendungslogik in `app/main.py`. |
| Schnittstellen nachvollziehbar machen | FastAPI erzeugt aus Typannotationen und Modellen eine OpenAPI-Spezifikation sowie Swagger UI und ReDoc. |

Für einen Einstieg in den Code bieten sich die [Datenmodelle](app/schemas.py) und anschließend die [API-Endpunkte](app/main.py) an.

## Funktionsumfang

- Beratungsanfragen anlegen; ID und initialer Status `neu` werden serverseitig gesetzt.
- Alle erfassten Anfragen auflisten.
- Anfragen nach vollständiger Postleitzahl oder einem PLZ-Präfix mit zwei bis fünf Zeichen filtern.
- Einzelne Anfragen über ihre positive numerische ID abrufen.
- Die vier fachlichen Angaben einer vorhandenen Anfrage vollständig ersetzen oder einzeln ändern; ID und Status bleiben erhalten.
- Vorhandene Anfragen löschen.

### API-Endpunkte

| Methode | Pfad | Funktion | Erfolgsstatus |
| --- | --- | --- | --- |
| `POST` | `/inquiries` | Anfrage anlegen | `201 Created` |
| `GET` | `/inquiries` | Alle Anfragen auflisten | `200 OK` |
| `GET` | `/inquiries?postal_code=70` | Anfragen nach PLZ-Präfix filtern | `200 OK` |
| `GET` | `/inquiries/{inquiry_id}` | Einzelne Anfrage abrufen | `200 OK` |
| `PUT` | `/inquiries/{inquiry_id}` | Alle vier fachlichen Felder ersetzen | `200 OK` |
| `PATCH` | `/inquiries/{inquiry_id}` | Einzelne fachliche Felder ändern | `200 OK` |
| `DELETE` | `/inquiries/{inquiry_id}` | Anfrage löschen; Antwort ohne Body | `204 No Content` |

### Datenvalidierung

| Eingabefeld | Regel |
| --- | --- |
| `customer_name` | Zeichenkette mit 2 bis 100 Zeichen |
| `postal_code` | Zeichenkette aus genau fünf Ziffern; führende Nullen bleiben erhalten |
| `kitchen_type` | Einer der Werte `zeile`, `l_form` oder `insel` |
| `budget` | Zahl größer als null |

POST und PUT verlangen alle vier Felder. Bei PATCH können Felder weggelassen werden; übermittelte Werte unterliegen denselben Regeln. Explizites `null` ist für diese Felder unzulässig. Ein leerer PATCH-Body `{}` lässt die Anfrage unverändert. Zusätzliche Eingabefelder wie `id` und `status` werden ignoriert. Für unbekannte positive IDs liefern GET, PUT, PATCH und DELETE HTTP `404`.

## Lokal starten

Voraussetzung ist eine Python-Installation mit `venv` und `pip`. Lokal wurde die Anwendung mit Python 3.12 geprüft.

Alle folgenden Befehle werden im Projektordner ausgeführt, also in dem Ordner, der `app/` und `requirements.txt` enthält.

### Windows / PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload
```

Nach dem Start stehen diese lokalen URLs bereit:

- Swagger UI zum Ausprobieren: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI-Spezifikation: <http://127.0.0.1:8000/openapi.json>

**Hinweis zum Start:** `app.main:app` bezeichnet das Python-Modul `app.main` und das darin definierte FastAPI-Objekt `app`. Starte die Anwendung mit dem Uvicorn-Befehl aus dem Projektordner. Ein direkter Aufruf von `app/main.py` kann zu `ModuleNotFoundError: No module named 'app'` führen.

## Beispiel: Eine Anfrage erfassen

In Swagger UI unter `POST /inquiries` auf **Try it out** klicken und diesen JSON-Body senden:

```json
{
  "customer_name": "Max Mustermann",
  "postal_code": "70173",
  "kitchen_type": "l_form",
  "budget": 15000
}
```

Antwort mit HTTP `201 Created` bei der ersten Anfrage nach einem frischen Start:

```json
{
  "customer_name": "Max Mustermann",
  "postal_code": "70173",
  "kitchen_type": "l_form",
  "budget": 15000.0,
  "id": 1,
  "status": "neu"
}
```

Die Anfrage lässt sich anschließend über `GET /inquiries/1` abrufen. `GET /inquiries?postal_code=70` liefert alle gespeicherten Anfragen, deren PLZ mit `70` beginnt. Ein Budget von `0` oder eine ungültige Küchenform führt zu HTTP `422`; eine unbekannte positive Anfrage-ID zu HTTP `404`.

### Eine Anfrage ändern und löschen

Mit `PUT /inquiries/1` sendest du alle vier fachlichen Felder im selben Format wie beim Anlegen. Der Server ersetzt diese Angaben und behält ID und Status bei. Eine noch nicht vorhandene ID wird dadurch nicht angelegt.

Für `PATCH /inquiries/1` genügt beispielsweise:

```json
{
  "budget": 18000
}
```

Die übrigen Angaben bleiben erhalten. `DELETE /inquiries/1` löscht die Anfrage und liefert HTTP `204` ohne Antwort-Body. Ein anschließender Abruf oder erneutes Löschen liefert `404`.

## Projektstruktur

```text
Anfrage-und-Beratungs-Workflows/
├── app/
│   ├── __init__.py      # Python-Paket
│   ├── main.py          # FastAPI-App, Endpunkte und In-Memory-Speicher
│   └── schemas.py       # Pydantic-Modelle und Küchenformen
├── requirements.txt    # Laufzeitabhängigkeiten
├── tests/              # Automatisierte HTTP-Integrationstests
├── README.md
└── LICENSE
```

## Aktueller Stand und mögliche Erweiterungen

Der Prototyp bildet Anlegen, Lesen, Ersetzen, Teiländerungen und Löschen ab. Die Daten liegen ausschließlich im Speicher des jeweiligen Serverprozesses und gehen bei einem Neustart oder automatischen Reload verloren. Mehrere Serverprozesse teilen sich diesen Speicher nicht. Eine dauerhafte Datenbank, Benutzeranmeldung sowie ein vollständiger Beratungsprozess sind bisher nicht implementiert.

Die automatisierten HTTP-Integrationstests starten einen eigenen lokalen Uvicorn-Prozess mit temporärem Port. Sie prüfen die Endpunkte einschließlich Validierung, unveränderter Daten bei fehlerhaften Änderungen und leerer DELETE-Antwort. Sie benötigen nur die Laufzeitabhängigkeiten und die Python-Standardbibliothek.

Unter Windows / PowerShell aus dem Projektordner ausführen:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Unter macOS / Linux entsprechend `.venv/bin/python -m unittest discover -s tests -v` verwenden.

Mögliche nächste Entwicklungsschritte:

- Dauerhafte Speicherung mit SQLite oder PostgreSQL.
- Tests um weitere fachliche Regeln und später die Datenbankintegration erweitern.
- Bearbeitungsstatus und Zuständigkeiten für die weitere Beratung.
- Authentifizierung und rollenbasierter Zugriff vor einem Einsatz mit echten Kundendaten.

## Lernmaterial

Die [Schritt-für-Schritt-Lernanleitung](docs/learning/2026-10-22_23-25_fastapi-inquiry-api-step-by-step.md) erklärt den Datenfluss, die Dateien und den Code mit Begründungen, Beispielen, Fehlersuche und Übungen.

## Lizenz

Das Projekt steht unter der [MIT-Lizenz](LICENSE).
