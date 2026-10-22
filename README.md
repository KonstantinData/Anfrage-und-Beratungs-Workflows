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
| REST-Schnittstellen entwickeln | POST- und GET-Endpunkte verwenden Ressourcenpfade, Pfadparameter und optionale Query-Parameter. |
| Eingaben validieren | Pydantic prüft Zeichenlängen, das PLZ-Format, erlaubte Küchenformen und ein positives Budget. |
| Eingabe und Ausgabe trennen | `InquiryCreate` beschreibt die Eingabe; `InquiryResponse` ergänzt die serverseitig erzeugten Felder `id` und `status`. |
| Fehlerfälle behandeln | Ungültige Eingaben führen zu HTTP `422`, unbekannte Anfragen zu HTTP `404`. |
| Code strukturieren | Datenmodelle liegen in `app/schemas.py`, Endpunkte und Anwendungslogik in `app/main.py`. |
| Schnittstellen nachvollziehbar machen | FastAPI erzeugt aus Typannotationen und Modellen eine OpenAPI-Spezifikation sowie Swagger UI und ReDoc. |

Für einen Einstieg in den Code bieten sich die [Datenmodelle](app/schemas.py) und anschließend die [API-Endpunkte](app/main.py) an.

## Funktionsumfang

- Beratungsanfragen anlegen; ID und initialer Status `neu` werden serverseitig gesetzt.
- Alle erfassten Anfragen auflisten.
- Anfragen nach vollständiger Postleitzahl oder einem PLZ-Präfix mit zwei bis fünf Zeichen filtern.
- Einzelne Anfragen über ihre positive numerische ID abrufen.

### API-Endpunkte

| Methode | Pfad | Funktion | Erfolgsstatus |
| --- | --- | --- | --- |
| `POST` | `/inquiries` | Anfrage anlegen | `201 Created` |
| `GET` | `/inquiries` | Alle Anfragen auflisten | `200 OK` |
| `GET` | `/inquiries?postal_code=70` | Anfragen nach PLZ-Präfix filtern | `200 OK` |
| `GET` | `/inquiries/{inquiry_id}` | Einzelne Anfrage abrufen | `200 OK` |

### Datenvalidierung

| Eingabefeld | Regel |
| --- | --- |
| `customer_name` | Zeichenkette mit 2 bis 100 Zeichen |
| `postal_code` | Zeichenkette aus genau fünf Ziffern; führende Nullen bleiben erhalten |
| `kitchen_type` | Einer der Werte `zeile`, `l_form` oder `insel` |
| `budget` | Zahl größer als null |

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

## Projektstruktur

```text
Anfrage-und-Beratungs-Workflows/
├── app/
│   ├── __init__.py      # Python-Paket
│   ├── main.py          # FastAPI-App, Endpunkte und In-Memory-Speicher
│   └── schemas.py       # Pydantic-Modelle und Küchenformen
├── requirements.txt    # Laufzeitabhängigkeiten
├── README.md
└── LICENSE
```

## Aktueller Stand und mögliche Erweiterungen

Der Prototyp bildet die Erfassung und Abfrage ab. Die Daten liegen ausschließlich im Speicher des jeweiligen Serverprozesses und gehen bei einem Neustart oder automatischen Reload verloren. Mehrere Serverprozesse teilen sich diesen Speicher nicht. Eine dauerhafte Datenbank, Benutzeranmeldung, Bearbeitungs- und Löschfunktionen sowie ein vollständiger Beratungsprozess sind bisher nicht implementiert.

Start, OpenAPI-Ausgabe, Anlegen und Abrufen von Anfragen, PLZ-Filter sowie Validierungs- und Fehlerfälle wurden lokal geprüft. Eine automatisierte Testsuite ist im Repository bisher nicht enthalten.

Mögliche nächste Entwicklungsschritte:

- Dauerhafte Speicherung mit SQLite oder PostgreSQL.
- Automatisierte Tests für Endpunkte, Validierungsregeln und Fehlerfälle.
- Bearbeitungsstatus und Zuständigkeiten für die weitere Beratung.
- Authentifizierung und rollenbasierter Zugriff vor einem Einsatz mit echten Kundendaten.

## Lizenz

Das Projekt steht unter der [MIT-Lizenz](LICENSE).
