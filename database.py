"""
Модуль для работы с базой данных SQLite.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple


class ReminderDB:
    """Класс для управления базой данных напоминаний."""
    
    def __init__(self, db_path: str = "reminders.db"):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_path: Путь к файлу базы данных.
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Создание подключения к базе данных."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def _create_tables(self):
        """Создание таблиц, если они не существуют."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                scheduled_at TEXT NOT NULL,
                status TEXT DEFAULT 'Ожидает'
            )
        """)
        self.conn.commit()
    
    def add_reminder(self, title: str, description: str, scheduled_at: str) -> int:
        """
        Добавление нового напоминания.
        
        Args:
            title: Заголовок напоминания.
            description: Описание напоминания.
            scheduled_at: Дата и время срабатывания (формат: YYYY-MM-DD HH:MM:SS).
            
        Returns:
            ID созданного напоминания.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (title, description, scheduled_at, status) VALUES (?, ?, ?, ?)",
            (title, description, scheduled_at, "Ожидает")
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_reminders(self) -> List[Tuple]:
        """
        Получение всех напоминаний.
        
        Returns:
            Список всех напоминаний.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reminders ORDER BY scheduled_at")
        return cursor.fetchall()
    
    def get_pending_reminders(self) -> List[Tuple]:
        """
        Получение напоминаний со статусом "Ожидает".
        
        Returns:
            Список ожидающих напоминаний.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE status = 'Ожидает' ORDER BY scheduled_at")
        return cursor.fetchall()
    
    def get_reminder_by_id(self, reminder_id: int) -> Optional[Tuple]:
        """
        Получение напоминания по ID.
        
        Args:
            reminder_id: ID напоминания.
            
        Returns:
            Напоминание или None, если не найдено.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        return cursor.fetchone()
    
    def update_reminder_status(self, reminder_id: int, status: str) -> bool:
        """
        Обновление статуса напоминания.
        
        Args:
            reminder_id: ID напоминания.
            status: Новый статус.
            
        Returns:
            True если успешно обновлено, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE reminders SET status = ? WHERE id = ?",
            (status, reminder_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_reminder_title(self, reminder_id: int, title: str) -> bool:
        """
        Обновление заголовка напоминания.
        
        Args:
            reminder_id: ID напоминания.
            title: Новый заголовок.
            
        Returns:
            True если успешно обновлено, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE reminders SET title = ? WHERE id = ?",
            (title, reminder_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
        
    def update_reminder_description(self, reminder_id: int, description: str) -> bool:
        """
        Обновление описания напоминания.
        
        Args:
            reminder_id: ID напоминания.
            description: Новое описание.
            
        Returns:
            True если успешно обновлено, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE reminders SET description = ? WHERE id = ?",
            (description, reminder_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_reminder_scheduled_at(self, reminder_id: int, scheduled_at: str) -> bool:
        """
        Обновление даты и времени напоминания.
        
        Args:
            reminder_id: ID напоминания.
            scheduled_at: Новая дата и время.
            
        Returns:
            True если успешно обновлено, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE reminders SET scheduled_at = ? WHERE id = ?",
            (scheduled_at, reminder_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """
        Удаление напоминания.
        
        Args:
            reminder_id: ID напоминания.
            
        Returns:
            True если успешно удалено, False иначе.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def check_overdue_reminders(self) -> List[Tuple]:
        """
        Проверка и обновление просроченных напоминаний.
        
        Returns:
            Список просроченных напоминаний.
        """
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "SELECT * FROM reminders WHERE status = 'Ожидает' AND scheduled_at < ?",
            (now,)
        )
        overdue = cursor.fetchall()
        
        # Обновляем статус на "Просрочено"
        cursor.execute(
            "UPDATE reminders SET status = 'Просрочено' WHERE status = 'Ожидает' AND scheduled_at < ?",
            (now,)
        )
        self.conn.commit()
        
        return overdue
    
    def close(self):
        """Закрытие подключения к базе данных."""
        if self.conn:
            self.conn.close()
