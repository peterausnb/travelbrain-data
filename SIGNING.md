# Manifest-Signierung

## Zielbild

Das veröffentlichte `manifest.json` wird später zusätzlich mit Ed25519 signiert. Die Android-App enthält ausschließlich den öffentlichen Schlüssel und verwirft Manifeste mit ungültiger Signatur.

## Schlüsseltrennung

- Der private Schlüssel darf niemals in Git, in Build-Artefakten oder in App-Dateien liegen.
- Er wird offline erzeugt und als geschütztes GitHub-Actions-Secret hinterlegt.
- Der öffentliche Schlüssel wird mit einer stabilen Schlüssel-ID im privaten App-Repository abgelegt.
- Für einen Schlüsselwechsel akzeptiert die App während einer Übergangszeit den alten und den neuen öffentlichen Schlüssel.

## Geplantes Veröffentlichungsformat

Neben `manifest.json` wird `manifest.sig.json` veröffentlicht:

```json
{
  "algorithm": "Ed25519",
  "keyId": "travelbrain-data-2026-01",
  "manifestSha256": "<sha256-hex>",
  "signature": "<base64>"
}
```

Signiert werden die exakten kanonischen Bytes von `manifest.json`. Die Signatur wird erst nach erfolgreicher Schema- und Inhaltsvalidierung erzeugt.

## Einführung

1. Offline Schlüsselpaar erzeugen und Wiederherstellungskopie sicher verwahren.
2. Privaten Schlüssel als geschütztes Repository-Secret hinterlegen.
3. Öffentlichen Schlüssel und Schlüssel-ID in TravelBrain ausliefern.
4. Signaturschritt und Negativtests in die Publishing-Pipeline aufnehmen.
5. Erst danach die Signaturprüfung in der App verpflichtend schalten.
