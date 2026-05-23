"""
Модуль управления стилями приложения.
"""


class Styles:
    """Класс с константами стилей приложения."""
    
    # Шрифты
    FONT_MAIN = ("Segoe UI", 10)
    FONT_MAIN_SMALL = ("Segoe UI", 9)
    FONT_MAIN_BOLD = ("Segoe UI", 10, "bold")
    FONT_TITLE = ("Segoe UI", 14, "bold")
    FONT_STATUS = ("Segoe UI", 9)
    
    # Размеры
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 550
    WINDOW_WIDTH_POPUP = 400
    WINDOW_HEIGHT_POPUP = 200
    WINDOW_WIDTH_DIALOG = 500
    WINDOW_HEIGHT_DIALOG = 450
    
    # Цвета фона - Контрастная тёмная тема
    BG_WINDOW = "#1E1E1E"        # Основной фон (чёрный)
    BG_STATUS_BAR = "#3C3C3C"    # Фон строки состояния (серый)
    BG_INPUT_FRAME = "#252526"   # Фон формы ввода
    BG_ENTRY = "#3C3C3C"         # Фон полей ввода
    BG_TABLE = "#1E1E1E"         # Фон таблицы (тёмный)
    BG_TREE_HEADER = "#2D2D2D"   # Фон заголовков таблицы
    
    # Цвета текста - белый для контраста
    TEXT_DEFAULT = "#AAA9A9"     # Основной текст
    TEXT_HIGHLIGHT = "#4EC9B0"   # Выделенный текст
    TEXT_MUTED = "#694949"       # Второстепенный текст
    
    # Цвета сообщений в строке состояния
    COLOR_SUCCESS = "#4EC9B0"    # Зелёный (успех)
    COLOR_WARNING = "#FFA500"    # Оранжевый (предупреждение)
    COLOR_ERROR = "#F44747"      # Красный (ошибка)
    COLOR_INFO = "#569CD6"       # Синий (инфо)
    
    # Цвета статусов в таблице
    STATUS_COLOR_PENDING = "#FFA500"   # Ожидает (оранжевый)
    STATUS_COLOR_COMPLETED = "#4EC9B0" # Готово (зелёный)
    STATUS_COLOR_OVERDUE = "#F44747"   # Просрочено (красный)
    STATUS_COLOR_CANCELLED = "#808080" # Отменено (серый)
    
    # Цвета кнопок
    BUTTON_BG = "#007ACC"        # Синий фон
    BUTTON_BG_HOVER = "#0098FF"  # Яркий синий при наведении
    BUTTON_FG = "#000000"        # Чёрный текст символов
    
    # Кнопки действий
    BUTTON_ADD_BG = "#4EC9B0"    # Зелёный для добавления
    BUTTON_ADD_HOVER = "#388E3C"
    BUTTON_EDIT_BG = "#007ACC"   # Синий для редактирования
    BUTTON_EDIT_HOVER = "#1976D2"
    BUTTON_DELETE_BG = "#F44747" # Красный для удаления
    BUTTON_DELETE_HOVER = "#D32F2F"
    BUTTON_REFRESH_BG = "#FFA500" # Оранжевый для обновления
    BUTTON_REFRESH_HOVER = "#F57C00"
    
    # Отступы
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    
    # Размеры полей ввода
    INPUT_WIDTH_LONG = 40
    INPUT_WIDTH_MEDIUM = 25
    
    # Кнопки
    BUTTON_WIDTH = 12
    
    # Таблица
    TABLE_COLUMN_ID_WIDTH = 50
    TABLE_COLUMN_TITLE_WIDTH = 150
    TABLE_COLUMN_DESC_WIDTH = 200
    TABLE_COLUMN_TIME_WIDTH = 150
    TABLE_COLUMN_STATUS_WIDTH = 100
    
    # Строка состояния
    STATUS_BAR_HEIGHT = 30


def get_button_style():
    """Возвращает параметры стиля кнопки."""
    return {
        "font": Styles.FONT_MAIN,
        "width": Styles.BUTTON_WIDTH,
        "bg": Styles.BUTTON_BG,
        "fg": Styles.BUTTON_FG
    }


def get_input_style():
    """Возвращает параметры стиля поля ввода."""
    return {
        "font": Styles.FONT_MAIN
    }


def get_label_style():
    """Возвращает параметры стиля метки."""
    return {
        "font": Styles.FONT_MAIN
    }


def get_status_label_style():
    """Возвращает параметры стиля строки состояния."""
    return {
        "font": Styles.FONT_STATUS,
        "bg": Styles.BG_STATUS_BAR,
        "fg": Styles.COLOR_INFO,
        "anchor": "w",
        "padx": Styles.PADDING_MEDIUM
    }
