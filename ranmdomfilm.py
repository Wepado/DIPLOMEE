import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import requests
import random
from time import sleep
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel,
                            QPushButton, QCheckBox, QScrollArea, QWidget,
                            QGridLayout, QHBoxLayout, QSpinBox, QComboBox,
                            QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from io import BytesIO
from loginwindow import LoginWindow
from UserRepository import UserRepository
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation




API_KEY = "6f6e8f0b05edebee7397c06568df4987"
PROXY = {
    'http': 'http://f6aHkEBV:jyRZSrZz@154.81.196.194:63984',
    'https': 'http://f6aHkEBV:jyRZSrZz@154.81.196.194:63984'
}
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


GENRES = {
    28: "Боевик",
    12: "Приключения",
    16: "Мультфильм",
    35: "Комедия",
    80: "Криминал",
    99: "Документальный",
    18: "Драма",
    10751: "Семейный",
    14: "Фэнтези",
    36: "История",
    27: "Ужасы",
    10402: "Музыка",
    9648: "Детектив",
    10749: "Мелодрама",
    878: "Фантастика",
    10770: "Телефильм",
    53: "Триллер",
    10752: "Военный",
    37: "Вестерн"
}

class MovieRandomizer:
    def __init__(self, username, user_repo):
        self.username = username
        self.user_repo = user_repo
        self.seen_movies = set(self.user_repo.get_seen_movies(username))
    
    def get_movie_details(self, movie_id, language="ru-RU"):
        """Получает детальную информацию о фильме на указанном языке"""
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}",
                params={
                    "api_key": API_KEY,
                    "language": language,
                },
                proxies=PROXY,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_random_movie(self, genres=None, total_pages=5, min_rating=0, year_from=None, year_to=None, exclude_seen=True):
        """Получает случайный фильм с учетом фильтров и многоязычным описанием"""
        try:
            all_movies = []
            
            
            params = {
                "api_key": API_KEY,
                "language": "ru-RU",
                "sort_by": "popularity.desc",
                "with_genres": ",".join(map(str, genres)) if genres else None,
                "vote_average.gte": min_rating,
                "page": 1
            }
            if year_from or year_to:
                if year_from and year_to:
                    params["primary_release_date.gte"] = f"{year_from}-01-01"
                    params["primary_release_date.lte"] = f"{year_to}-12-31"
                elif year_from:
                    params["primary_release_date.gte"] = f"{year_from}-01-01"
                elif year_to:
                    params["primary_release_date.lte"] = f"{year_to}-12-31" 
            initial_response = requests.get(
                "https://api.themoviedb.org/3/discover/movie",
                params=params,
                proxies=PROXY,
                timeout=15
            )
            initial_response.raise_for_status()
            data = initial_response.json()
            total_pages_available = min(data.get("total_pages", 1), total_pages)
            for page in range(1, total_pages_available + 1):
                params["page"] = page
                try:
                    response = requests.get(
                        "https://api.themoviedb.org/3/discover/movie",
                        params=params,
                        proxies=PROXY,
                        timeout=15
                    )
                    response.raise_for_status()
                    movies = response.json().get("results", [])
                    
                    
                    if exclude_seen:
                        movies = [m for m in movies if m.get('id') not in self.seen_movies]
                    
                    all_movies.extend(movies)
                except requests.exceptions.RequestException:
                    continue
            
            if not all_movies:
                return None
            chosen_movie = random.choice(all_movies)
            if not chosen_movie.get('overview'):
                en_movie = self.get_movie_details(chosen_movie['id'], "en-US")
                if en_movie and en_movie.get('overview'):
                    chosen_movie['overview'] = en_movie['overview']
                    chosen_movie['original_language'] = 'en'
            if exclude_seen:
                self.seen_movies.add(chosen_movie.get('id'))
            return chosen_movie
        except Exception as e:
            print(f"Error: {e}")
            return None

class MovieApp(QMainWindow):    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.repo = UserRepository()  # 🆕 создаём репозиторий
        self.movie_randomizer = MovieRandomizer(self.username, self.repo)  # 🆕 передаём его в рандомайзер
        self.dark_theme_enabled = False
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("🍿 Кинорандомайзер ")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QLabel { font-size: 14px; }
            QPushButton { 
                font-size: 16px; 
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QCheckBox { font-size: 13px; spacing: 5px; }
            QScrollArea { border: none; }
            QSpinBox, QLineEdit { padding: 5px; font-size: 14px; }
            QGroupBox { 
                border: 1px solid #ddd; 
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)


        # Заголовок
        title = QLabel(" Кинорандомайзер ")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Группа настроек
        settings_group = QGroupBox("Настройки поиска")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)

        
        
        # Количество страниц
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Страниц для поиска:"))
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 20)
        self.pages_spin.setValue(5)
        pages_layout.addWidget(self.pages_spin)
        pages_layout.addStretch()
        settings_layout.addLayout(pages_layout)
        
        # Фильтр по рейтингу
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("Минимальный рейтинг:"))
        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(0, 10)
        self.rating_spin.setValue(6)
        rating_layout.addWidget(self.rating_spin)
        rating_layout.addStretch()
        settings_layout.addLayout(rating_layout)
        
        # Фильтр по году
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Годы выпуска:"))
        self.year_from_edit = QLineEdit()
        self.year_from_edit.setPlaceholderText("От (год)")
        self.year_from_edit.setMaximumWidth(80)
        year_layout.addWidget(self.year_from_edit)
        
        year_layout.addWidget(QLabel("—"))
        
        self.year_to_edit = QLineEdit()
        self.year_to_edit.setPlaceholderText("До (год)")
        self.year_to_edit.setMaximumWidth(80)
        year_layout.addWidget(self.year_to_edit)
        year_layout.addStretch()
        settings_layout.addLayout(year_layout)
        
        # Исключать просмотренные
        self.exclude_seen_cb = QCheckBox("Исключать уже показанные фильмы")
        self.exclude_seen_cb.setChecked(True)
        settings_layout.addWidget(self.exclude_seen_cb)
        
        layout.addWidget(settings_group)
        
        # Группа жанров
        genres_group = QGroupBox("Выберите жанры (можно несколько)")
        genres_layout = QVBoxLayout()
        genres_group.setLayout(genres_layout)
        
        # Сетка чекбоксов
        grid = QGridLayout()
        genre_widget = QWidget()
        genre_widget.setLayout(grid)
        
        self.genre_boxes = []
        for i, (genre_id, genre_name) in enumerate(GENRES.items()):
            cb = QCheckBox(genre_name)
            self.genre_boxes.append((genre_id, cb))
            grid.addWidget(cb, i//3, i%3)
        
        # Прокручиваемая область для чекбоксов
        scroll = QScrollArea()
        scroll.setWidget(genre_widget)
        scroll.setWidgetResizable(True)
        genres_layout.addWidget(scroll)
        layout.addWidget(genres_group)
        
        # Кнопка поиска
        self.search_btn = QPushButton("🎬 Найти фильм")
        self.search_btn.clicked.connect(self.find_movie)
        layout.addWidget(self.search_btn)
        
        self.history_btn = QPushButton("🕘 История фильмов")
        self.history_btn.clicked.connect(self.show_history)
        layout.addWidget(self.history_btn)

        self.theme_btn = QPushButton("🎨 Сменить тему")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)
        # Контейнер для результата
        self.result_container = QWidget()
        self.result_layout = QHBoxLayout()
        self.result_container.setLayout(self.result_layout)
        
        # Текстовое описание
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_layout.addWidget(self.result_label, stretch=2)
        
        # Виджет для постера
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.poster_label.setMinimumWidth(300)
        self.poster_label.setMaximumWidth(350)
        self.poster_label.setScaledContents(True)
        self.poster_label.setMaximumHeight(500)
        self.poster_label.setMinimumHeight(300)
        self.result_layout.addWidget(self.poster_label, stretch=1)
        
        result_scroll = QScrollArea()
        result_scroll.setWidget(self.result_container)
        result_scroll.setWidgetResizable(True)
        layout.addWidget(result_scroll)
    
    def find_movie(self):
        selected_genres = [gid for gid, cb in self.genre_boxes if cb.isChecked()]
        if not selected_genres:
            self.result_label.setText("<h3 style='color: red;'>Выберите хотя бы один жанр!</h3>")
            self.poster_label.clear()
            return
        self.search_btn.setText("Ищем фильмы...")
        self.search_btn.setEnabled(False)
        QApplication.processEvents()
        min_rating = self.rating_spin.value()
        year_from = self.year_from_edit.text().strip() or None
        year_to = self.year_to_edit.text().strip() or None
        movie = self.movie_randomizer.get_random_movie(
            genres=selected_genres,
            total_pages=self.pages_spin.value(),
            min_rating=min_rating,
            year_from=year_from,
            year_to=year_to,
            exclude_seen=self.exclude_seen_cb.isChecked()
        )
        if movie:
            poster_path = movie.get('poster_path')
            if poster_path:
                try:
                    response = requests.get(
                        f"{BASE_IMAGE_URL}{poster_path}",
                        proxies=PROXY,
                        timeout=10
                    )
                    img_data = BytesIO(response.content)
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data.getvalue())
                    scaled_pixmap = pixmap.scaled(
                        self.poster_label.width(),
                        self.poster_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.poster_label.setPixmap(scaled_pixmap)
                    self.animate_widget_fade_in(self.poster_label)
                except Exception:
                    self.poster_label.setText("<i>Не удалось загрузить постер</i>")
            else:
                self.poster_label.setText("<i>Постер отсутствует</i>")
            genres = ", ".join(GENRES[gid] for gid in movie.get('genre_ids', []))
            description = movie.get('overview', 'Нет описания')
            lang_note = "" if not movie.get('overview') or movie.get('original_language') == 'ru' else "<br><i>(Описание на английском)</i>"
            text = (
                f"<h2 style='margin-top: 0; color: #2c3e50;'>{movie.get('title', 'Без названия')}</h2>"
                f"<p><b>⭐ Рейтинг:</b> {movie.get('vote_average', '?')}/10</p>"
                f"<p><b>📅 Год выхода:</b> {movie.get('release_date', '????')[:4]}</p>"
                f"<p><b>🏷 Жанры:</b> {genres}</p>"
                f"<hr style='border: 1px solid #eee;'>"
                f"<p><b>📖 Сюжет:</b><br>{description}{lang_note}</p>"
                f"<p style='margin-bottom: 0;'><a href='https://www.themoviedb.org/movie/{movie.get('id', '')}'>"
                f"🔗 Подробнее на TMDB</a></p>"
            )
            self.result_label.setText(text)
        else:
            self.result_label.setText(
                "<h3 style='color: red;'>Не удалось найти фильм по вашим критериям. "
                "Попробуйте изменить параметры поиска.</h3>"
            )
            self.poster_label.clear()
        self.search_btn.setText("🎬 Найти фильм")
        self.search_btn.setEnabled(True)
        self.repo.add_seen_movie(self.username, movie['id'])

    def show_history(self):
        movies = self.repo.get_seen_movies_info(self.username)

        if not movies:
            QMessageBox.information(self, "История", "У вас пока нет просмотренных фильмов.")
            return

        text = ""
        for m in movies:
            text += f"🎬 {m['title']} ({m['year']}) — ⭐ {m['rating']}/10\n"

        QMessageBox.information(self, f"История — {self.username}", text)

    def toggle_theme(self):
        self.dark_theme_enabled = not self.dark_theme_enabled
        self.apply_theme()
    def apply_theme(self):
        if self.dark_theme_enabled:
            self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #eeeeee; }
            QLabel { font-size: 14px; color: #eeeeee; }
            QPushButton { 
                font-size: 16px; 
                padding: 8px;
                background-color: #444;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #555; }
            QCheckBox { font-size: 13px; color: #ddd; }
            QSpinBox, QLineEdit { 
                padding: 5px; 
                font-size: 14px; 
                background: #3a3a3a; 
                color: #fff; 
                border: 1px solid #666; 
            }
            QGroupBox {
                border: 1px solid #444; 
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #eee;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

            self.result_label.setStyleSheet("""
            QLabel {
                background-color: #3a3a3a;
                color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            a { color: #66aaff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
            self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #444;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        else:
            self.setStyleSheet(""" 
            QLabel { font-size: 14px; }
            QPushButton { 
                font-size: 16px; 
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QCheckBox { font-size: 13px; spacing: 5px; }
            QScrollArea { border: none; }
            QSpinBox, QLineEdit { padding: 5px; font-size: 14px; }
            QGroupBox { 
                border: 1px solid #ddd; 
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

            self.result_label.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8;
                color: #000000;
                padding: 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
            self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                padding: 10px;
                border-radius: 8px;
            }
        """)
    def animate_widget_fade_in(self, widget, duration=500):

        if hasattr(widget, "_animation") and widget._animation is not None:
            widget._animation.stop()
            del widget._animation

        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()

        widget._animation = anim  


if __name__ == "__main__":
    app = QApplication([])

    # Сохраняем глобальную ссылку на окно
    main_window = None

    def start_app(username):
        global main_window
        main_window = MovieApp(username)
        main_window.show()

    login_window = LoginWindow(on_login_success=start_app)
    login_window.show()

    sys.exit(app.exec())
