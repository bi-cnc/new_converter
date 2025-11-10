import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

def get_rates_for_date(date):
    date_str = date.strftime("%d.%m.%Y")
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/index.html?date={date_str}"
    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        return None

    rows = table.find_all("tr")
    rates = {"date": date.strftime("%Y-%m-%d"), "CZK": {"rate": 1, "quantity": 1}}

    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) >= 5:
            try:
                quantity = float(cells[2].text.replace("\xa0", "").strip())
                code = cells[3].text.strip()
                rate = float(cells[4].text.replace("\xa0", "").replace(",", ".").strip())
                rates[code] = {"rate": rate, "quantity": quantity}
            except Exception:
                continue
    return rates

# 🕒 zkus aktuální datum, případně posouvej zpět max o 5 dní
today = datetime.now()
for i in range(5):
    check_date = today - timedelta(days=i)
    rates = get_rates_for_date(check_date)
    if rates:
        break

if not rates:
    raise RuntimeError("Nepodařilo se načíst žádné kurzy za posledních 5 dní.")

# 💾 uložení
os.makedirs("data", exist_ok=True)
with open(f"data/{rates['date']}.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)

with open("data/latest.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)

print(f"✅ Načteno {len(rates)-2} měn pro {rates['date']}")
