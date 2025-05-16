import os
from datetime import datetime

def log_interaction(update, response):
    user = update.effective_user
    user_id = user.id
    folder = "logs"
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/{user_id}.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {user.full_name} ({user_id})\n")
        f.write(f"User: {update.message.text}\n")
        f.write(f"Bot: {response}\n\n")
