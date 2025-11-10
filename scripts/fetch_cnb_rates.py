import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

today = datetime.now()
date_str = today.strftime("%d.%m.%Y")
output_date = today.strftime("%Y-%m-%d")

url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/index.html?date={date_str}"

r = requests.get(url)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")
table = soup.find("table")
rows = table.find_all("tr")

rates = {"date": output_date, "CZK": {"rate": 1, "quantity": 1}}

for row in rows[1:]:
    cells = row.find_all("td")
    if len(cells) >= 5:
        try:
            quantity = float(cells[2].text.replace("\xa0", "").strip())
            code = cells[3].text.strip()
            rate = float(cells[4].text.replace("\xa0", "").replace(",", ".").strip())
            rates[code] = {"rate": rate, "quantity": quantity}
        except:
            continue

os.makedirs("data", exist_ok=True)
with open(f"data/{output_date}.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)

# Zkopíruj jako "latest.json"
with open("data/latest.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)
