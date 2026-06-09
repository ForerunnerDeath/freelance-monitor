import requests
from bs4 import BeautifulSoup


url = "https://www.fl.ru/projects/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=10)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a")

for link in links:
    href = link.get("href")

    if href is None:
        continue

    if not href.startswith("/projects/"):
        continue

    parts = href.split("/")

    if len(parts) <= 2:
        continue

    external_id = parts[2]

    if not external_id.isdigit():
        continue

    print("-----")
    print("href:", href)
    print("external_id:", external_id)
    print("text:", link.text.strip())

    card = link.parent.parent.parent

    print("card tag:", card.name)
    print("card class:", card.get("class"))
    print("card id:", card.get("id"))

    card_text = card.get_text("\n", strip=True)
    print("----- CARD TEXT -----")
    print(card_text)
    lines = card_text.split("\n")
    for index, line in enumerate(lines):
        print(index, "=>", line)
    title_from_card = lines[0] if len(lines) > 0 else ""
    budget_from_card = lines[1] if len(lines) > 1 else ""
    description_from_card = lines[2] if len(lines) > 2 else ""
    print("title:", title_from_card)
    print("budget:", budget_from_card)
    print("description:", description_from_card)

    break