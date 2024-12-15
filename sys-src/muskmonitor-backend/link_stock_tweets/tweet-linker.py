import json

# JSON-Daten einlesen
with open('konvertierte_datei.json', 'r') as file:
    data = json.load(file)

# Funktion, um große Kursunterschiede zu finden
def find_large_price_differences(data, threshold=20):
    result = []

    for i in range(1, len(data)):
        prev_day = data[i - 1]
        curr_day = data[i]

        open_diff = abs(curr_day['open'] - prev_day['open'])
        close_diff = abs(curr_day['close'] - prev_day['close'])

        if open_diff > threshold or close_diff > threshold:
            result.append({
                'Datum': curr_day['Datum'],
                'openDiff': open_diff,
                'closeDiff': close_diff,
            })

    return result

# Große Kursunterschiede finden
large_differences = find_large_price_differences(data)

# Nur speichern, wenn die Differenz größer als 10 war
if large_differences:
    # Ergebnis in eine JSON-Datei schreiben
    with open('large_differences.json', 'w') as outfile:
        json.dump(large_differences, outfile, indent=4)
    print('Ergebnis wurde in large_differences.json gespeichert.')
else:
    print('Keine großen Kursunterschiede gefunden.')