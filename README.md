# TravelBrain Data

Öffentliche, redaktionell gepflegte Länderinformationen für die Android-App **TravelBrain**.

> **Projektstatus:** MVP-Datenbestand aufgebaut. Die vorgesehenen 20 europäischen MVP-Länder sowie Transitkorridore sind redaktionell angelegt; freigegebene Inhalte werden automatisiert validiert, gebaut und veröffentlicht.

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
docs/                      dokumentierte Quellenentscheidungen
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

Nach Aktivierung von GitHub Pages mit der Quelle **GitHub Actions** veröffentlicht jeder Merge nach `main` automatisch das Manifest, die freigegebenen Länderpakete und die Transitkorridore unter `https://peterausnb.github.io/travelbrain-data/`.

Version und Erstellungszeit werden aus dem auslösenden Commit abgeleitet. Ein erneut ausgeführter Build desselben Laufs erzeugt dadurch identische Dateien. Die App prüft vor der Übernahme die im Manifest hinterlegten SHA-256-Werte.

Die vorbereitete zusätzliche ECDSA-P-256-Signatur ist in [SIGNING.md](SIGNING.md) beschrieben. Bis zur kontrollierten Aktivierung mit einem extern erzeugten Produktionsschlüssel gilt HTTPS plus SHA-256-Prüfung als MVP-Transportabsicherung.

## Lizenz

Die redaktionellen TravelBrain-Inhalte stehen unter [CC BY 4.0](LICENSE.md). Quellmaterial Dritter bleibt unter dessen eigener Lizenz beziehungsweise dessen Nutzungsbedingungen.
