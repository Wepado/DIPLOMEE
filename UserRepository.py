import json
import os
import requests
API_KEY = "6f6e8f0b05edebee7397c06568df4987"
PROXY = {
    'http': 'http://f6aHkEBV:jyRZSrZz@154.81.196.194:63984',
    'https': 'http://f6aHkEBV:jyRZSrZz@154.81.196.194:63984'
}
class UserRepository:
    def __init__(self, file_path="users.json"):
        self.file_path = file_path
        self.users = self.load_users()
    def load_users(self):
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    def save_users(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)
    def add_user(self, username, password):
        if any(user["username"] == username for user in self.users):
            return False
        self.users.append({
            "username": username,
            "password": password,
            "seen_movies": []
        })
        self.save_users()
        return True
    def validate_user(self, username, password):
        return any(user["username"] == username and user["password"] == password for user in self.users)
    def get_seen_movies(self, username):
        for user in self.users:
            if user["username"] == username:
                return user.get("seen_movies", [])
        return []
    def add_seen_movie(self, username, movie_id):
        for user in self.users:
            if user["username"] == username:
                if "seen_movies" not in user:
                    user["seen_movies"] = []
                if movie_id not in user["seen_movies"]:
                    user["seen_movies"].append(movie_id)
                    self.save_users()
    def get_seen_movies_info(self, username):
        movie_ids = self.get_seen_movies(username)
        movies = []

        for movie_id in movie_ids:
            try:
                response = requests.get(
                    f"https://api.themoviedb.org/3/movie/{movie_id}",
                    params={"api_key": API_KEY, "language": "ru-RU"},
                    proxies=PROXY,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                movies.append({
                    "title": data.get("title", "Без названия"),
                    "rating": data.get("vote_average", "?"),
                    "year": data.get("release_date", "????")[:4]
                })
            except:
                continue
        return movies
