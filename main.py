"""
Точка входа в приложение-напоминалку.
"""
from gui import ReminderApp


def main():
    """Главная функция запуска приложения."""
    app = ReminderApp()
    app.run()


if __name__ == "__main__":
    main()
