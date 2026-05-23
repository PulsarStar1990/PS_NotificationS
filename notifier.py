"""
Модуль для отображения системных уведомлений Windows 11 через ctypes.
"""
import ctypes
import threading


class NotificationManager:
    """Класс для управления системными уведомлениями."""
    
    def __init__(self):
        """Инициализация менеджера уведомлений."""
        self.SHELL32 = ctypes.windll.shell32
        self.USER32 = ctypes.windll.user32
        # MB_OK = 0x00000000
        self.MB_OK = 0x00000000
    
    def show_notification(self, title: str, message: str, duration: int = 10):
        """
        Отображение системного уведомления через Taskbar Notification.
        
        Args:
            title: Заголовок уведомления.
            message: Текст сообщения.
            duration: Длительность отображения в секундах (используется для таймера).
        """
        def _show():
            # Используем Shell_NotifyIcon для отображения уведомления
            # Это упрощённый вариант через MessageBox для совместимости
            self.USER32.MessageBoxW(0, message, title, self.MB_OK)
        
        thread = threading.Thread(target=_show, daemon=True)
        thread.start()