import requests
from bs4 import BeautifulSoup

def fetch_orders():

    url = "https://www.fl.ru/projects/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    seen_ids = set()
    orders = []

    for link in links:
        href = link.get("href")
        if href is None:
            continue
        if href.startswith("/projects/"):
            parts = href.split("/")
            if len(parts) > 2:
                external_id = parts[2]
                if not external_id.isdigit():
                    continue
                if external_id in seen_ids:
                    continue
                seen_ids.add(external_id)

                text = link.text.strip()
                full_url = "https://www.fl.ru" + href
                order = {
                    "source": "fl_ru",
                    "external_id": external_id,
                    "title": text,
                    "url": full_url,
                    "description": "",
                    "budget": "",
                    "tags": [],
                }
                orders.append(order)
    return orders


if __name__ == "__main__":
    orders = fetch_orders()

    print("Найдено заказов:", len(orders))

    for order in orders[:5]:
        print(order["external_id"], order["title"], order["url"])
