import json
import requests
from bs4 import BeautifulSoup


# Функция для получения информации на сайте film.ru
def get_top_films(year: int, top_n: int = 5) -> str:
    url = f"https://www.film.ru/a-z/movies/{year}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)  # Получение html кода страницы
        response.raise_for_status()
    except requests.RequestException:
        return "⚠️ Не удалось загрузить данные с сайта."

    soup = BeautifulSoup(response.text, "html.parser")
    script_tags = soup.find_all("script", type="application/ld+json")  # Поиск тегов которые содержат json-данные
    for script in script_tags:
        if "ItemList" in script.text and f"{year}" in script.text:  # Поиск <script>, в котором есть список фильмов по ключу "ItemList" и году
            try:
                data = json.loads(script.string)  # Превращение в словарь
                films = data.get("itemListElement", [])[:top_n]  # Поиск ключа и срез данных
                if not films:
                    return "❌ Не найдено фильмов."

                # Формирование вывода
                result = f"*Топ-{top_n} фильмов {year} года:*\n"
                for item in films:
                    movie = item["item"]
                    title = movie.get("name")
                    url = movie.get("url")
                    result += f"🎬 [{title}]({url})\n"
                return result
            except json.JSONDecodeError:
                continue

    return "❌ Не удалось найти фильмы за этот год."


def scrape_kinopoisk(title):
    search_url = f"https://www.kinopoisk.ru/index.php?kp_query={title}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers)  # Получение html кода страницы

        soup = BeautifulSoup(response.content, "html.parser")
        first_result = soup.select_one(".search_results .element.most_wanted")  # Поиск информации по селекторам

        if not first_result:
            return "Фильм не найден на Кинопоиске."
        name_tag = first_result.select_one("p.name a")  # Поиск по CSS-селектору
        name = name_tag.text.strip()
        link = "https://www.kinopoisk.ru" + name_tag["href"]

        # Извлечение рейтинга из div class="rating ratingGreenBG"
        rating_tag = first_result.select_one("div.rating.ratingGreenBG")
        rating = rating_tag.text.strip() if rating_tag else "Нет рейтинга"

        return f"🎬 {name}\n⭐ Рейтинг: {rating}\n🔗 {link}"

    except Exception as e:
        return f"Ошибка скрапинга: {str(e)}"
