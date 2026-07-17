# Manifest-Signierung

## Zielbild

Das veröffentlichte `manifest.json` wird zusätzlich mit ECDSA auf der Kurve P-256 und SHA-256 signiert. Die Android-App enthält ausschließlich den öffentlichen Schlüssel und verwirft Manifeste mit ungültiger Signatur. Das Verfahren ist ohne zusätzliche Kryptobibliothek im gesamten vorgesehenen Android-Zielbereich ab API 26 verfügbar.

## Schlüsseltrennung

- Der private Schlüssel darf niemals in Git, in Build-Artefakten oder in App-Dateien liegen.
- Er wird offline erzeugt, verschlüsselt gesichert und in unverschlüsselter PEM-Darstellung ausschließlich als geschütztes GitHub-Actions-Secret hinterlegt.
- Der öffentliche Schlüssel wird mit einer stabilen Schlüssel-ID im privaten App-Repository abgelegt.
- Für einen Schlüsselwechsel akzeptiert die App während einer Übergangszeit den alten und den neuen öffentlichen Schlüssel.

## Geplantes Veröffentlichungsformat

Neben `manifest.json` wird `manifest.sig.json` veröffentlicht:

```json
{
  "schemaVersion": 1,
  "algorithm": "ECDSA_P256_SHA256",
  "keyId": "travelbrain-data-2026-01",
  "manifestSha256": "<sha256-hex>",
  "signature": "<base64-kodierte DER-Signatur>"
}
```

Signiert werden die exakten Bytes von `manifest.json`. Die Signatur wird erst nach erfolgreicher Schema- und Inhaltsvalidierung erzeugt. `scripts/sign_manifest.py` prüft Schlüsseltyp und Kurve, signiert, verifiziert das Ergebnis unmittelbar und erzeugt die Signaturdatei kanonisch.

## Produktionsschlüssel erzeugen

Die folgenden Befehle werden auf einem vertrauenswürdigen, nicht gemeinsam genutzten Rechner ausgeführt:

```bash
umask 077
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out travelbrain-data-2026-01.pem
openssl pkey -in travelbrain-data-2026-01.pem -check -noout
openssl pkey -in travelbrain-data-2026-01.pem -pubout -out travelbrain-data-2026-01-public.pem
openssl pkey -in travelbrain-data-2026-01.pem -aes-256-cbc -out travelbrain-data-2026-01-backup.pem
```

- Die verschlüsselte Backup-Datei und ihr Kennwort werden getrennt verwahrt.
- Der private PEM-Inhalt wird als Repository-Secret `TRAVELBRAIN_SIGNING_KEY_PEM` hinterlegt.
- Die ID `travelbrain-data-2026-01` wird als Repository-Variable `TRAVELBRAIN_SIGNING_KEY_ID` hinterlegt.
- Der öffentliche Schlüssel wird vor Aktivierung der Signierung X.509-kodiert in eine veröffentlichte TravelBrain-App-Version aufgenommen.
- Private Schlüsseldateien werden niemals committet, als Build-Artefakt hochgeladen oder in Logs ausgegeben.

Ist nur Secret oder Variable gesetzt, bricht die Publishing-Pipeline ab. Sind beide noch nicht gesetzt, veröffentlicht sie während der Einführungsphase weiterhin ohne Signatur.

## Einführung

1. Signaturschritt und Negativtests in die Publishing-Pipeline aufnehmen.
2. Offline Schlüsselpaar erzeugen und Wiederherstellungskopie sicher verwahren.
3. Öffentlichen Schlüssel und Schlüssel-ID in TravelBrain ausliefern.
4. Privaten Schlüssel und Schlüssel-ID in GitHub konfigurieren und Veröffentlichung prüfen.
5. Erst danach die Signaturprüfung in der App verpflichtend schalten.

Bei einer Rotation akzeptiert zunächst eine App-Version den alten und den neuen öffentlichen Schlüssel. Erst danach wechselt die Pipeline auf die neue Schlüssel-ID. Der alte Schlüssel wird nach einer Übergangszeit aus einer späteren App-Version entfernt.
