import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup

def scrape_upcoming_movies():
    url = "https://www.kinopoisk.ru/lists/movies/planned-to-watch-films/"

    # Настройки для headless режима
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Запускаем Chrome
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Даем время на загрузку JS-контента
    time.sleep(5)

    # Получаем HTML
    html = driver.page_source
    driver.quit()

    # Парсим HTML
    soup = BeautifulSoup(html, "html.parser")
    movies = soup.find_all("img", class_="styles_image__gRXvn")

    if not movies:
        return "Не удалось найти ожидаемые фильмы на Кинопоиске."

    result = []
    for movie in movies[:10]:
        title = movie.get("alt")
        if title:
            result.append(f"🎬 {title}")

    return "\n".join(result)


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
