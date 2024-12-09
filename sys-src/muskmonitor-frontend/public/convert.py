import json
from datetime import datetime

# Erste Datei laden
with open('historical_data.json', 'r', encoding='utf-8') as f:
    erste_datei = json.load(f)

# Konvertierte Daten
konvertierte_daten = []

# Konvertierung durchführen
for eintrag in erste_datei:
    datum = datetime.strptime(eintrag["Datum"], '%m/%d/%Y').strftime('%Y-%m-%d')
    konvertierte_daten.append({
        "Datum": datum,
        "open": float(eintrag["Eröffnungskurs"].replace('$', '').replace(',', '')),
        "high": float(eintrag["Hoch"].replace('$', '').replace(',', '')),
        "low": float(eintrag["Tief"].replace('$', '').replace(',', '')),
        "close": float(eintrag["Schluss/Letzter"].replace('$', '').replace(',', '')),
        "volume": int(eintrag["Volumen"])
    })

# Konvertierte Daten in eine neue Datei speichern
with open('konvertierte_datei.json', 'w', encoding='utf-8') as f:
    json.dump(konvertierte_daten, f, indent=4)

print("Die Daten wurden erfolgreich konvertiert und in 'konvertierte_datei.json' gespeichert.")