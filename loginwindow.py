from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from UserRepository import UserRepository

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.setWindowTitle("Вход / Регистрация")
        self.repo = UserRepository()
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Пароль")
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("Регистрация")
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if self.repo.validate_user(username, password):
            self.on_login_success(username)
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if self.repo.add_user(username, password):
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован!")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует.")
