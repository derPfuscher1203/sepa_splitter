# SEPA-XML-Datei splitten

Dieses kleine Python-Skript teilt eine bereits erzeugte SEPA-Lastschriftdatei in mehrere gültige XML-Dateien auf.

Gedacht für den Fall, dass eine Vereins- oder Verwaltungssoftware eine große SEPA-Datei erzeugt, die Bank aber nur eine begrenzte Anzahl von Buchungen pro Datei akzeptiert.

## Dateityp

Das Skript ist für SEPA-Lastschriften im Format:

```xml
pain.008.001.02
```

also z. B.:

```xml
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02">
```

## Dateien

Im Arbeitsordner sollten liegen:

```text
sepa_split.py
SEPA_DATEI.xml
```

`SEPA_DATEI.xml` steht hier als Platzhalter für die von der Software erzeugte Originaldatei.

## Vorbereitung

Python muss installiert sein. Unter Windows kann Python z. B. mit `winget` installiert werden.

Test in PowerShell:

```powershell
py --version
```

Wenn eine Python-Version angezeigt wird, ist alles bereit.

## Verwendung

PowerShell im Ordner mit den Dateien öffnen:

```powershell
cd "C:\Pfad\zum\SEPA-Ordner"
```

Alte Teildateien löschen, damit nichts verwechselt wird:

```powershell
del *_teil_*.xml
```

SEPA-Datei splitten:

```powershell
py sepa_split.py SEPA_DATEI.xml
```

Danach entstehen neue Dateien, z. B.:

```text
SEPA_DATEI_teil_001.xml
SEPA_DATEI_teil_002.xml
```

## Was das Skript macht

Das Skript:

- übernimmt die vorhandene SEPA-Datei als Grundlage,
- teilt die einzelnen Lastschriften in Blöcke mit maximal 999 Buchungen,
- aktualisiert pro Teildatei die Anzahl der Buchungen,
- berechnet die Summe je Teildatei neu,
- passt `MsgId` und `PmtInfId` eindeutig an,
- achtet darauf, dass diese IDs maximal 35 Zeichen lang bleiben.

## Warum 999 und nicht 1000?

Wenn die Bank maximal 1000 Buchungen erlaubt, verwendet das Skript bewusst 999 Buchungen pro Datei, um Grenzfälle zu vermeiden.

## Ausgabe prüfen

Nach dem Erzeugen zeigt das Skript pro Datei etwa Folgendes an:

```text
Erzeugt: SEPA_DATEI_teil_001.xml | Buchungen: 999 | Summe: 12345.67
Erzeugt: SEPA_DATEI_teil_002.xml | Buchungen: 137 | Summe: 1234.56
```

Vor dem Hochladen prüfen:

- Stimmen die Summen ungefähr?
- Stimmen die Buchungszahlen?
- Wird wirklich nur die geteilte Datei hochgeladen?
- Die Originaldatei nicht zusätzlich hochladen.

## Upload bei der Bank

Im Bankportal werden anschließend die erzeugten Teildateien einzeln hochgeladen:

```text
..._teil_001.xml
..._teil_002.xml
...
```

## Häufige Fehler

### Python meldet „Non-UTF-8 code“

Dann wurde `sepa_split.py` nicht als UTF-8 gespeichert.

Lösung: Datei in einem Editor öffnen und als **UTF-8** speichern.

Am Anfang der Datei sollte stehen:

```python
# -*- coding: utf-8 -*-
```

### Bank meldet „XML-Dokument ist nicht gültig“

Mögliche Ursachen:

- alte Teildatei wurde hochgeladen,
- `MsgId` oder `PmtInfId` ist zu lang,
- die Originaldatei hat eine besondere Struktur,
- das Bankportal zeigt nur eine allgemeine Fehlermeldung.

Dann im Bankportal nach Details, Fehlerprotokoll oder Zeilennummer suchen.

Hilfreich sind genaue Meldungen wie:

```text
Element ... ist nicht erwartet
Wert ist länger als maximal erlaubt
Invalid content was found starting with element ...
```

## Sicherheit

Die Originaldatei sollte immer unverändert aufbewahrt werden.

Empfohlenes Vorgehen:

1. Originaldatei sichern.
2. Teildateien erzeugen.
3. Summen und Anzahl prüfen.
4. Teildateien einzeln hochladen.
5. Originaldatei nicht hochladen.

## Beispiel

```powershell
cd "C:\Pfad\zum\SEPA-Ordner"
del *_teil_*.xml
py sepa_split.py SEPA_DATEI.xml
```
