# TravelBrain Data

Öffentliche, redaktionell gepflegte Länderinformationen für die Android-App **TravelBrain**.

> **Projektstatus:** Aufbauphase. Italien sowie die Transitpakete Österreich und Schweiz sind erstmals freigegeben; weitere Länder folgen schrittweise.

## Grundsätze

- YAML-Dateien unter `countries/` und `corridors/` sind die redaktionelle Quelle der Wahrheit.
- Nur fachlich freigegebene Inhalte mit `review.status: approved` gelangen in `dist/`.
- Kritische Aussagen benötigen auflösbare Quellenreferenzen.
- Persönliche Reisen, Profile und Dokumentdaten gehören niemals in dieses Repository.
- Wetter, Wechselkurse und aktuelle Reisewarnungen werden nicht als statische Länderfakten gepflegt.
- Amtliche Texte werden verlinkt und in eigenen Worten knapp zusammengefasst, nicht vollständig kopiert.

## Struktur

```text
countries/                 Länderdateien als YAML
corridors/                 redaktionelle Transitkorridore
schemas/                   JSON Schemas
shared/                    gemeinsame Codelisten
scripts/                   Validierung und Build
tests/                     Pipeline-Tests
dist/                      generierte App-Dateien, nicht manuell bearbeiten
.github/workflows/         Pull-Request- und Veröffentlichungsprüfung
```

## Lokal prüfen

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/build.py
python -m unittest discover -s tests
```

Der Build erzeugt nur freigegebene Länder und Korridore. Entwürfe bleiben vollständig aus `dist/` ausgeschlossen.

## Veröffentlichungsweg

1. Inhalt in einem Branch ändern.
2. Quellen und Prüfdaten ergänzen.
3. Pull Request erstellen.
4. Automatische Validierung abwarten.
5. Fachlich prüfen und `review.status` erst dann auf `approved` setzen.
6. Nach Merge wird ein neues statisches Paket gebaut.

GitHub Pages wird erst aktiviert, nachdem Schema, Signierung und die ersten freigegebenen Länder gemeinsam geprüft wurden.

## Lizenz

Die redaktionellen TravelBrain-Inhalte stehen unter [CC BY 4.0](LICENSE.md). Quellmaterial Dritter bleibt unter dessen eigener Lizenz beziehungsweise dessen Nutzungsbedingungen.
