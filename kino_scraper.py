import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup



import requests
from bs4 import BeautifulSoup

def get_top_films(year: int, top_n: int = 5) -> str:
    url = f"https://www.film.ru/a-z/movies/{year}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        return "⚠️ Не удалось загрузить данные с сайта."

    soup = BeautifulSoup(response.text, "html.parser")
    script_tags = soup.find_all("script", type="application/ld+json")

    for script in script_tags:
        if "ItemList" in script.text and f"{year}" in script.text:
            import json
            try:
                data = json.loads(script.string)
                films = data.get("itemListElement", [])[:top_n]
                if not films:
                    return "❌ Не найдено фильмов."

                result = f"*Топ-{top_n} фильмов {year} года:*\n"
                for item in films:
                    movie = item["item"]
                    title = movie.get("name", "Без названия")
                    url = movie.get("url", "")
                    result += f"🎬 [{title}]({url})\n"
                return result
            except json.JSONDecodeError:
                continue

    return "❌ Не удалось найти фильмы за этот год."



def scrape_kinopoisk(title):
    search_url = f"https://www.kinopoisk.ru/index.php?kp_query={title}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)


        soup = BeautifulSoup(response.content, "html.parser")
        first_result = soup.select_one(".search_results .element.most_wanted")

        if not first_result:
            return "Фильм не найден на Кинопоиске."

        name_tag = first_result.select_one("p.name a")
        name = name_tag.text.strip()
        link = "https://www.kinopoisk.ru" + name_tag["href"]

        # Извлекаем рейтинг из <div class="rating ratingGreenBG">
        rating_tag = first_result.select_one("div.rating.ratingGreenBG")
        rating = rating_tag.text.strip() if rating_tag else "Нет рейтинга"

        return f"🎬 {name}\n⭐ Рейтинг: {rating}\n🔗 {link}"

    except Exception as e:
        return f"Ошибка скрапинга: {str(e)}"
