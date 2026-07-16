# Mitwirken

## Inhaltsänderungen

Jede fachliche Änderung erfolgt über einen Pull Request und beschreibt:

- betroffene Länder und Module
- fachliche Änderung
- verwendete Primärquellen
- Abrufdatum
- Grund der Änderung
- mögliche Auswirkung auf Aufgaben oder Warnungen

## Quellen

- Behörden, EU-Portale und offizielle Betreiber werden bevorzugt.
- Längere Fremdtexte werden nicht kopiert.
- Jede kritische Aussage verweist über `sourceRefs` auf einen Eintrag in `sources`.
- Redaktionelle Konventionen müssen als solche klassifiziert sein.

## Freigabe

Nur fachlich geprüfte Dateien erhalten `review.status: approved`. Ein Autor soll die eigene sicherheitskritische Änderung nicht allein freigeben.

## Technische Regeln

- keine manuelle Änderung unter `dist/`
- stabile IDs nicht ohne Migrationshinweis ändern
- Schemaänderungen getrennt von Inhaltsänderungen vornehmen
- keine persönlichen Daten oder Geheimnisse einchecken
