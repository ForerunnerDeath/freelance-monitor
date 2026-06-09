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

                card = link.parent.parent.parent
                card_text = card.get_text("\n", strip=True)
                lines = card_text.split("\n")
                title_from_card = lines[0] if len(lines) > 0 else ""
                budget_from_card = lines[1] if len(lines) > 1 else ""

                if len(lines) > 2 and lines[2] == "руб":
                    budget_from_card = budget_from_card + " " + lines[2]
                    description_from_card = lines[3] if len(lines) > 3 else ""
                else:
                    description_from_card = lines[2] if len(lines) > 2 else ""

                project_type = ""
                if "Откликнуться" in lines:
                    button_index = lines.index("Откликнуться")
                    project_type = lines[button_index + 1] if (button_index + 1) < len(lines) else ""


                full_url = "https://www.fl.ru" + href
                order = {
                    "source": "fl_ru",
                    "external_id": external_id,
                    "title": title_from_card,
                    "url": full_url,
                    "description": description_from_card,
                    "budget": budget_from_card,
                    "tags": [],
                    "project_type": project_type,
                }
                orders.append(order)
    return orders


if __name__ == "__main__":
    orders = fetch_orders()

    print("Найдено заказов:", len(orders))

    for order in orders[:5]:
        print("-----")
        print("ID:", order["external_id"])
        print("Title:", order["title"])
        print("Budget:", order["budget"])
        print("Description:", order["description"])
        print("URL:", order["url"])
        print("Type:", order["project_type"])
