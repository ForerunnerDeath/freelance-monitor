import asyncio
import httpx
from bs4 import BeautifulSoup

import config


def parse_project_card(card):
    link = card.find("a")
    if link is None:
        return None
    href = link.get("href")
    if href is None:
        return None
    url = "https://www.fl.ru" + href
    text = card.get_text("\n", strip=True)
    lines = text.splitlines()
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
    return {
        "title": title_from_card,
        "url": url,
        "budget": budget_from_card,
        "description": description_from_card,
        "project_type": project_type,
        "lines": lines,
        }


def build_projects_url(page):
    if page == 1:
        return "https://www.fl.ru/projects/"
    else:
        return f"https://www.fl.ru/projects/page-{page}/"


def parse_page_html(html, page, verbose=True):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    seen_ids = set()
    orders = []

    project_links_count = 0
    bad_id_count = 0
    duplicate_link_count = 0
    bad_parent_count = 0
    parse_none_count = 0

    for link in links:
        href = link.get("href")
        if href is None:
            continue

        if href.startswith("/projects/"):
            project_links_count += 1
            parts = href.split("/")
            if len(parts) > 2:
                external_id = parts[2]
                if not external_id.isdigit():
                    bad_id_count += 1
                    continue
                if external_id in seen_ids:
                    duplicate_link_count += 1
                    continue
                seen_ids.add(external_id)
                parent1 = link.parent
                if parent1 is None:
                    bad_parent_count += 1
                    continue
                parent2 = parent1.parent
                if parent2 is None:
                    bad_parent_count += 1
                    continue
                parent3 = parent2.parent
                if parent3 is None:
                    bad_parent_count += 1
                    continue
                card = parent3
                project = parse_project_card(card)
                if project is None:
                    parse_none_count += 1
                    continue

                order = {
                    "source": "fl_ru",
                    "external_id": external_id,
                    "title": project["title"],
                    "url": project["url"],
                    "description": project["description"],
                    "budget": project["budget"],
                    "tags": [],
                    "project_type": project["project_type"],
                }
                orders.append(order)
    if len(orders) < config.FL_RU_MIN_ORDERS_PER_PAGE:
        print("Предупреждение: FL.ru page", page, "вернула мало заказов:", len(orders))
    if verbose:
        print("FL.ru page", page, "links =", project_links_count, "bad_id =", bad_id_count, "duplicates =", duplicate_link_count, "bad_parent =", bad_parent_count, "parse_none =", parse_none_count, "orders =", len(orders))
    return orders


async def fetch_page(client, semaphore, page, verbose=True):
    url = build_projects_url(page)
    headers = {
        "User-Agent": config.FL_RU_USER_AGENT
    }
    async with semaphore:
        try:
            response = await client.get(
                url,
                headers=headers,
                timeout=config.FL_RU_TIMEOUT,
            )
        except httpx.HTTPError as error:
            print("Сетевая ошибка:", error)
            return []
    if response.status_code != 200:
        print("Ошибка HTTP FL.ru", response.status_code, url)
        return []
    return parse_page_html(response.text, page, verbose=verbose)


async def fetch_orders_async(pages=1, verbose=True):
    semaphore = asyncio.Semaphore(config.FL_RU_CONCURRENCY_LIMIT)

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_page(client, semaphore, page, verbose=verbose)
            for page in range(1, pages + 1)
        ]
        results = await asyncio.gather(*tasks)
    
    all_orders = []

    for page, page_orders in enumerate(results, start=1):
        if verbose:
            print("Страница", page, ":", "получено", len(page_orders), "заказов")
        all_orders.extend(page_orders)

    return all_orders


def fetch_orders(pages=1, verbose=True):
    return asyncio.run(fetch_orders_async(pages=pages, verbose=verbose))


if __name__ == "__main__":
    orders = fetch_orders(pages=3)
    print("Найдено заказов:", len(orders))

    for order in orders[:5]:
        print("-----")
        print("ID:", order["external_id"])
        print("Title:", order["title"])
        print("Budget:", order["budget"])
        print("URL:", order["url"])
        print("Type:", order["project_type"])
