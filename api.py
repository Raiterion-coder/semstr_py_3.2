import requests
from dotenv import load_dotenv
import random
import json
import os

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_random_quote():
    file_path = os.path.join(os.path.dirname(__file__), "quotes.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            quotes = json.load(f)
        if not quotes:
            return "Цитаты не найдены."
        quote_data = random.choice(quotes)
        return f"💬 \"{quote_data['quote']}\"\n🎭 {quote_data['character']}\n🎬 {quote_data['movie']}"
    except Exception as e:
        return f"Ошибка при загрузке цитат: {str(e)}"


def get_rating(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("Response") == "False":
        return None

    ratings_list = data.get("Ratings", [])
    if not ratings_list:
        return None

    ratings_lines = []
    for r in ratings_list:
        source = r['Source']
        value = r['Value']

        if source == "Internet Movie Database":
            # IMDB: "8.7/10" -> преобразуем в 0-5 звёзд
            imdb_rating = float(value.split('/')[0])
            stars = round(imdb_rating / 2)  # преобразуем 0-10 в 0-5
            star_str = "★" * stars + "☆" * (5 - stars)
            ratings_lines.append(f"⭐IMDb: {star_str} ({value})")

        elif source == "Rotten Tomatoes":
            # Rotten Tomatoes: "73%" -> преобразуем в 0-5 звёзд
            rt_rating = int(value.replace('%', ''))
            stars = round(rt_rating / 20)  # преобразуем 0-100 в 0-5
            star_str = "★" * stars + "☆" * (5 - stars)
            ratings_lines.append(f"⭐Rotten Tomatoes: {star_str} ({value})")

        elif source == "Metacritic":
            # Metacritic: "74/100" -> преобразуем в 0-5 звёзд
            mc_rating = int(value.split('/')[0])
            stars = round(mc_rating / 20)  # преобразуем 0-100 в 0-5
            star_str = "★" * stars + "☆" * (5 - stars)
            ratings_lines.append(f"⭐Metacritic: {star_str} ({value})")

        else:
            # Для других источников выводим как есть
            ratings_lines.append(f"{source}: {value}")

    return "\n".join(ratings_lines)


def get_summary(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("Response") == "False":
        return None
    plot = data.get("Plot")
    if not plot or plot == "N/A":
        return None
    return f"📃Описание фильма {title}📃 \n {plot}"


def get_random_film():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=RU-US&page=1"
    response = requests.get(url).json()
    total_pages = response.get('total_pages', 1)

    random_page = random.randint(1, min(total_pages, 500))
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={random_page}"
    response = requests.get(url).json()

    films = response.get('results', [])
    if not films:
        return "Не удалось получить фильмы."

    random_film = random.choice(films)
    random_title = random_film['title']
    random_year = random_film.get('release_date', '')[:4]  # например, 2020

    summary = get_summary(random_title)
    rating = get_rating(random_title)

    result = f"🎬 {random_title}"
    if random_year:
        result += f" ({random_year})"
    result += "\n"

    if summary:
        result += f"{summary}\n"

    if rating:
        result += f"\n{rating}"

    return result
