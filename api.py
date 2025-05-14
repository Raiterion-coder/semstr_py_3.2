import os
import requests
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_rating(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return "Ошибка при запросе к API."
    data = r.json()
    if data.get("Response") == "False":
        return f"Фильм не найден: {title}"
    ratings = "\n".join([f"{r['Source']}: {r['Value']}" for r in data.get("Ratings", [])])
    return f"🎬 {data['Title']} ({data['Year']})\n{ratings or 'Рейтинги не найдены.'}"

def get_summary(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return "Ошибка при запросе к API."
    data = r.json()
    if data.get("Response") == "False":
        return f"Фильм не найден: {title}"
    return f"🎬 {data['Title']} ({data['Year']})\n📃 {data['Plot']}"


import random

def get_random_film():
    films = [
        "Inception", "The Matrix", "Interstellar", "The Godfather",
        "Pulp Fiction", "Fight Club", "The Shawshank Redemption",
        "Forrest Gump", "The Dark Knight", "Gladiator"
    ]
    random_title = random.choice(films)
    return get_summary(random_title) + "\n\n" + get_rating(random_title)
