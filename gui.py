"""
Графический интерфейс и основная логика приложения.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

from database import ReminderDB
from notifier import NotificationManager
from styles import Styles


class ReminderPopupNonBlocking:
    """Всплывающее окно без блокировки главного цикла."""
    
    def __init__(self, title: str, description: str, on_complete_callback, parent_root):
        """Создание popup-окна без блокировки."""
        self.on_complete_callback = on_complete_callback
        
        self.popup = tk.Toplevel(parent_root)
        self.popup.title("Напоминание")
        self.popup.geometry(f"{Styles.WINDOW_WIDTH_POPUP}x{Styles.WINDOW_HEIGHT_POPUP}")
        self.popup.attributes('-topmost', True)
        self.popup.resizable(False, False)
        self.popup.protocol("WM_DELETE_WINDOW", self.on_complete)
        self.popup.configure(bg=Styles.BG_WINDOW)
        
        self.popup.update_idletasks()
        width = self.popup.winfo_width()
        height = self.popup.winfo_height()
        x = (self.popup.winfo_screenwidth() // 2) - (width // 2)
        y = (self.popup.winfo_screenheight() // 2) - (height // 2)
        self.popup.geometry(f'{width}x{height}+{x}+{y}')
        
        self._create_widgets(title, description)
    
    def _create_widgets(self, title: str, description: str):
        """Создание элементов интерфейса popup-окна."""
        title_label = tk.Label(
            self.popup,
            text=title,
            font=Styles.FONT_TITLE,
            wraplength=Styles.WINDOW_WIDTH_POPUP - 20,
            bg=Styles.BG_WINDOW,
            fg=Styles.TEXT_DEFAULT
        )
        title_label.pack(pady=(Styles.PADDING_LARGE, Styles.PADDING_MEDIUM))
        
        desc_label = tk.Label(
            self.popup,
            text=description if description else "Нет описания",
            font=("Segoe UI", 11),
            wraplength=Styles.WINDOW_WIDTH_POPUP - 20,
            bg=Styles.BG_WINDOW,
            fg=Styles.TEXT_MUTED
        )
        desc_label.pack(pady=(0, Styles.PADDING_LARGE))
        
        btn_frame = tk.Frame(self.popup, bg=Styles.BG_WINDOW)
        btn_frame.pack(pady=Styles.PADDING_MEDIUM)
        
        complete_btn = tk.Button(
            btn_frame,
            text="Выполнено",
            command=self.on_complete,
            font=Styles.FONT_MAIN,
            width=Styles.BUTTON_WIDTH,
            bg=Styles.BUTTON_ADD_BG,
            fg=Styles.BUTTON_FG
        )
        complete_btn.pack(side=tk.LEFT, padx=Styles.PADDING_SMALL)
        complete_btn.bind("<Enter>", lambda e: complete_btn.config(bg=Styles.BUTTON_ADD_HOVER))
        complete_btn.bind("<Leave>", lambda e: complete_btn.config(bg=Styles.BUTTON_ADD_BG))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Отменить",
            command=self.on_cancel,
            font=Styles.FONT_MAIN,
            width=Styles.BUTTON_WIDTH,
            bg=Styles.BUTTON_DELETE_BG,
            fg=Styles.BUTTON_FG
        )
        cancel_btn.pack(side=tk.LEFT, padx=Styles.PADDING_SMALL)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=Styles.BUTTON_DELETE_HOVER))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=Styles.BUTTON_DELETE_BG))
    
    def on_complete(self):
        """Обработчик кнопки 'Выполнено'."""
        if self.on_complete_callback:
            self.on_complete_callback("Готово")
        self.popup.destroy()
    
    def on_cancel(self):
        """Обработчик кнопки 'Отменить'."""
        if self.on_complete_callback:
            self.on_complete_callback("Отменено")
        self.popup.destroy()


class ReminderApp:
    """Основное приложение напоминаний."""
    
    def __init__(self):
        """Инициализация приложения."""
        self.db = ReminderDB()
        self.notifier = NotificationManager()
        self.root = tk.Tk()
        self.root.title("Напоминалка")
        self.root.geometry(f"{Styles.WINDOW_WIDTH}x{Styles.WINDOW_HEIGHT}")
        self.root.configure(bg=Styles.BG_WINDOW)
        
        self._running = True
        self._status_timer = None
        self._tooltip = None
        
        self._create_widgets()
        self._start_checking_thread()
        self._refresh_reminders()
    
    def _create_widgets(self):
        """Создание элементов интерфейса."""
        top_frame = tk.Frame(self.root, pady=Styles.PADDING_MEDIUM, padx=Styles.PADDING_MEDIUM, bg=Styles.BG_WINDOW)
        top_frame.pack(fill=tk.X)
        
        input_frame = tk.Frame(top_frame, bg=Styles.BG_INPUT_FRAME)
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
        
        # Заголовок
        tk.Label(input_frame, text="Заголовок:", font=Styles.FONT_MAIN, bg=Styles.BG_INPUT_FRAME, fg=Styles.TEXT_DEFAULT, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, pady=Styles.PADDING_SMALL)
        self.title_entry = tk.Entry(input_frame, font=Styles.FONT_MAIN, width=Styles.INPUT_WIDTH_LONG, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT, justify=tk.LEFT)
        self.title_entry.grid(row=0, column=1, padx=Styles.PADDING_SMALL, pady=Styles.PADDING_SMALL, sticky=tk.W)
        
        # Описание (многострочное на 5 строк)
        tk.Label(input_frame, text="Описание:", font=Styles.FONT_MAIN, bg=Styles.BG_INPUT_FRAME, fg=Styles.TEXT_DEFAULT, anchor=tk.W).grid(row=1, column=0, sticky=tk.W, pady=Styles.PADDING_SMALL)
        self.desc_text = tk.Text(input_frame, font=Styles.FONT_MAIN, width=Styles.INPUT_WIDTH_LONG, height=5, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT, wrap=tk.WORD)
        self.desc_text.grid(row=1, column=1, padx=Styles.PADDING_SMALL, pady=Styles.PADDING_SMALL, sticky=tk.W)
        
        # Дата
        tk.Label(input_frame, text="Дата:", font=Styles.FONT_MAIN, bg=Styles.BG_INPUT_FRAME, fg=Styles.TEXT_DEFAULT, anchor=tk.W).grid(row=2, column=0, sticky=tk.W, pady=Styles.PADDING_SMALL)
        self.date_entry = tk.Entry(input_frame, font=Styles.FONT_MAIN, width=15, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT, justify=tk.LEFT)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=Styles.PADDING_SMALL, pady=Styles.PADDING_SMALL, sticky=tk.W)
        
        # Время
        tk.Label(input_frame, text="Время:", font=Styles.FONT_MAIN, bg=Styles.BG_INPUT_FRAME, fg=Styles.TEXT_DEFAULT, anchor=tk.W).grid(row=3, column=0, sticky=tk.W, pady=Styles.PADDING_SMALL)
        self.time_entry = tk.Entry(input_frame, font=Styles.FONT_MAIN, width=10, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT, justify=tk.LEFT)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.grid(row=3, column=1, padx=Styles.PADDING_SMALL, pady=Styles.PADDING_SMALL, sticky=tk.W)
        
        # Кнопки
        btn_frame = tk.Frame(top_frame, bg=Styles.BG_WINDOW)
        btn_frame.pack(side=tk.RIGHT, padx=Styles.PADDING_MEDIUM)
        
        self.add_btn = tk.Button(btn_frame, text="➕", command=self._add_reminder, font=("Segoe MDL2 Assets", 12), width=3, relief=tk.FLAT, bg=Styles.BUTTON_ADD_BG, fg=Styles.BUTTON_FG, cursor="hand2")
        self.add_btn.pack(side=tk.TOP, pady=Styles.PADDING_SMALL)
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.config(bg=Styles.BUTTON_ADD_HOVER))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.config(bg=Styles.BUTTON_ADD_BG))
        self.add_btn.tooltip_text = "Добавить"
        
        self.edit_btn = tk.Button(btn_frame, text="🔄", command=self._edit_reminder, font=("Segoe MDL2 Assets", 12), width=3, relief=tk.FLAT, bg=Styles.BUTTON_EDIT_BG, fg=Styles.BUTTON_FG, cursor="hand2")
        self.edit_btn.pack(side=tk.TOP, pady=Styles.PADDING_SMALL)
        self.edit_btn.bind("<Enter>", lambda e: self.edit_btn.config(bg=Styles.BUTTON_EDIT_HOVER))
        self.edit_btn.bind("<Leave>", lambda e: self.edit_btn.config(bg=Styles.BUTTON_EDIT_BG))
        self.edit_btn.tooltip_text = "Обновить"
        
        self.delete_btn = tk.Button(btn_frame, text="🗑️", command=self._delete_reminder, font=("Segoe MDL2 Assets", 12), width=3, relief=tk.FLAT, bg=Styles.BUTTON_DELETE_BG, fg=Styles.BUTTON_FG, cursor="hand2")
        self.delete_btn.pack(side=tk.TOP, pady=Styles.PADDING_SMALL)
        self.delete_btn.bind("<Enter>", lambda e: self.delete_btn.config(bg=Styles.BUTTON_DELETE_HOVER))
        self.delete_btn.bind("<Leave>", lambda e: self.delete_btn.config(bg=Styles.BUTTON_DELETE_BG))
        self.delete_btn.tooltip_text = "Удалить"
        
        self.refresh_btn = tk.Button(btn_frame, text="📋", command=self._refresh_reminders, font=("Segoe MDL2 Assets", 12), width=3, relief=tk.FLAT, bg=Styles.BUTTON_REFRESH_BG, fg=Styles.BUTTON_FG, cursor="hand2")
        self.refresh_btn.pack(side=tk.TOP, pady=Styles.PADDING_SMALL)
        self.refresh_btn.bind("<Enter>", lambda e: self.refresh_btn.config(bg=Styles.BUTTON_REFRESH_HOVER))
        self.refresh_btn.bind("<Leave>", lambda e: self.refresh_btn.config(bg=Styles.BUTTON_REFRESH_BG))
        self.refresh_btn.tooltip_text = "Обновить список"
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            btn.bind("<Enter>", lambda e, b=btn: self._show_tooltip(b))
            btn.bind("<Leave>", lambda e: self._hide_tooltip())
        
        # Таблица
        table_frame = tk.Frame(self.root, bg=Styles.BG_WINDOW)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=Styles.PADDING_MEDIUM, pady=Styles.PADDING_MEDIUM)
        
        columns = ("ID", "Заголовок", "Описание", "Время", "Статус")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Заголовок", text="Заголовок")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Время", text="Время срабатывания")
        self.tree.heading("Статус", text="Статус")
        
        self.tree.column("ID", width=Styles.TABLE_COLUMN_ID_WIDTH)
        self.tree.column("Заголовок", width=Styles.TABLE_COLUMN_TITLE_WIDTH)
        self.tree.column("Описание", width=Styles.TABLE_COLUMN_DESC_WIDTH)
        self.tree.column("Время", width=Styles.TABLE_COLUMN_TIME_WIDTH)
        self.tree.column("Статус", width=Styles.TABLE_COLUMN_STATUS_WIDTH)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настраиваем стиль таблицы для тёмной темы
        style = ttk.Style()
        style.configure("Custom.Treeview", background=Styles.BG_TABLE, foreground=Styles.TEXT_DEFAULT, fieldbackground=Styles.BG_TABLE, rowheight=25)
        style.configure("Custom.Treeview.Heading", background=Styles.BG_TREE_HEADER, foreground=Styles.TEXT_DEFAULT, font=Styles.FONT_MAIN_BOLD)
        style.map("Custom.Treeview", background=[('selected', Styles.COLOR_INFO)], foreground=[('selected', Styles.TEXT_DEFAULT)])
        
        # Строка состояния
        self.status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bg=Styles.BG_STATUS_BAR, height=Styles.STATUS_BAR_HEIGHT)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="Готово", font=Styles.FONT_STATUS, bg=Styles.BG_STATUS_BAR, fg=Styles.TEXT_DEFAULT, anchor=tk.W, padx=Styles.PADDING_MEDIUM)
        self.status_label.pack(fill=tk.X, pady=Styles.PADDING_SMALL)
    
    def _show_tooltip(self, button):
        """Показ всплывающей подсказки."""
        if hasattr(self, '_tooltip') and self._tooltip and self._tooltip.winfo_exists():
            self._tooltip.destroy()
        
        self._tooltip = tk.Toplevel(self.root)
        self._tooltip.title("")
        self._tooltip.overrideredirect(True)
        self._tooltip.attributes('-topmost', True)
        self._tooltip.configure(bg=Styles.BG_WINDOW)
        
        x = self.root.winfo_rootx() + button.winfo_rootx() + button.winfo_width() + 10
        y = self.root.winfo_rooty() + button.winfo_rooty()
        self._tooltip.geometry(f"+{x}+{y}")
        
        tooltip_frame = tk.Frame(self._tooltip, bg=Styles.BG_STATUS_BAR, padx=Styles.PADDING_MEDIUM, pady=Styles.PADDING_SMALL)
        tooltip_frame.pack()
        
        tk.Label(tooltip_frame, text=button.tooltip_text, font=Styles.FONT_MAIN_BOLD, fg=Styles.TEXT_DEFAULT, bg=Styles.BG_STATUS_BAR).pack()
        
        self._tooltip.after(2000, self._hide_tooltip)
    
    def _hide_tooltip(self):
        """Скрытие всплывающей подсказки."""
        if hasattr(self, '_tooltip') and self._tooltip and self._tooltip.winfo_exists():
            self._tooltip.destroy()
            self._tooltip = None
    
    def _set_status(self, message: str, color: str, auto_reset: bool = True):
        """Установка сообщения в строке состояния."""
        if self._status_timer:
            self.root.after_cancel(self._status_timer)
        
        self.status_label.config(text=message, fg=color)
        
        if auto_reset:
            self._status_timer = self.root.after(3000, self._reset_status)
    
    def _reset_status(self):
        """Сброс строки состояния."""
        self.status_label.config(text="Готово", fg=Styles.COLOR_INFO)
        self._status_timer = None
    
    def _convert_reminder_to_tuple(self, reminder):
        """Преобразование sqlite3.Row в кортеж."""
        if reminder is None:
            return None
        return (int(reminder[0]), str(reminder[1]), str(reminder[2]) if reminder[2] else "", str(reminder[3]), str(reminder[4]))
    
    def _refresh_reminders(self):
        """Обновление списка напоминаний."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        reminders = self.db.get_all_reminders()
        for reminder in reminders:
            reminder_tuple = self._convert_reminder_to_tuple(reminder)
            self.tree.insert("", tk.END, values=reminder_tuple)
        
        self._set_status(f"Всего напоминаний: {len(reminders)}", Styles.COLOR_INFO, auto_reset=False)
    
    def _add_reminder(self):
        """Добавление напоминания."""
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        scheduled_at = f"{date_str} {time_str}:00"
        
        if not title:
            self._set_status("Ошибка: Заголовок обязателен!", Styles.COLOR_ERROR)
            return
        
        try:
            datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            self._set_status("Ошибка: Неверный формат даты!", Styles.COLOR_ERROR)
            return
        
        self.db.add_reminder(title, description, scheduled_at)
        self._refresh_reminders()
        
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        
        self._set_status("Напоминание добавлено", Styles.COLOR_SUCCESS)
    
    def _edit_reminder(self):
        """Редактирование напоминания."""
        selected = self.tree.selection()
        if not selected:
            self._set_status("Ошибка: Выберите напоминание для редактирования", Styles.COLOR_ERROR)
            return
        
        item = self.tree.item(selected[0])
        values = item["values"]
        reminder_id = int(values[0])
        
        dialog = EditReminderDialog(self.root, reminder_id, values[1], values[2], values[3], self._on_reminder_updated)
        dialog.root.wait_window()
    
    def _on_reminder_updated(self, reminder_id: int, title: str, description: str, scheduled_at: str):
        """Обработчик обновления напоминания."""
        self.db.update_reminder_title(reminder_id, title)
        self.db.update_reminder_description(reminder_id, description)
        self.db.update_reminder_scheduled_at(reminder_id, scheduled_at)
        self._refresh_reminders()
        self._set_status("Напоминание обновлено", Styles.COLOR_SUCCESS)
    
    def _delete_reminder(self):
        """Удаление напоминания."""
        selected = self.tree.selection()
        if not selected:
            self._set_status("Ошибка: Выберите напоминание для удаления", Styles.COLOR_ERROR)
            return
        
        item = self.tree.item(selected[0])
        values = item["values"]
        reminder_id = int(values[0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это напоминание?"):
            self.db.delete_reminder(reminder_id)
            self._refresh_reminders()
            self._set_status("Напоминание удалено", Styles.COLOR_WARNING)
    
    def _start_checking_thread(self):
        """Запуск фоновой проверки напоминаний."""
        def check_loop():
            while self._running:
                time.sleep(30)
                if self._running:
                    self._check_reminders()
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
    
    def _check_reminders(self):
        """Проверка напоминаний на срабатывание."""
        overdue = self.db.check_overdue_reminders()
        for reminder in overdue:
            reminder_tuple = self._convert_reminder_to_tuple(reminder)
            self.notifier.show_notification("Напоминание просрочено!", f"{reminder_tuple[1]}\n{reminder_tuple[2] or ''}", duration=10)
        
        pending = self.db.get_pending_reminders()
        now = datetime.now()
        
        for reminder in pending:
            reminder_tuple = self._convert_reminder_to_tuple(reminder)
            reminder_id = reminder_tuple[0]
            title = reminder_tuple[1]
            description = reminder_tuple[2]
            scheduled_at = reminder_tuple[3]
            
            try:
                scheduled_time = datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S")
                if scheduled_time <= now:
                    def on_complete_callback(new_status, rid=reminder_id):
                        self.db.update_reminder_status(rid, new_status)
                        self.root.after(0, self._refresh_reminders)
                    
                    self.root.after(0, lambda t=title, d=description, cb=on_complete_callback: self._show_popup_nonblocking(t, d, cb))
            except ValueError:
                continue
    
    def _show_popup_nonblocking(self, title: str, description: str, callback):
        """Показ всплывающего окна."""
        popup = ReminderPopupNonBlocking(title, description, callback, self.root)
    
    def run(self):
        """Запуск приложения."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Обработчик закрытия приложения."""
        self._running = False
        if self._status_timer:
            self.root.after_cancel(self._status_timer)
        self._hide_tooltip()
        self.db.close()
        self.root.destroy()


class EditReminderDialog:
    """Диалоговое окно редактирования напоминания."""
    
    def __init__(self, parent, reminder_id: int, title: str, description: str, scheduled_at: str, callback):
        self.reminder_id = reminder_id
        self.callback = callback
        self.root = tk.Toplevel(parent)
        self.root.title("Редактировать напоминание")
        self.root.geometry(f"{Styles.WINDOW_WIDTH_DIALOG}x{Styles.WINDOW_HEIGHT_DIALOG}")
        self.root.resizable(False, False)
        self.root.configure(bg=Styles.BG_WINDOW)
        
        try:
            dt = datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S")
            self.current_date = dt.strftime("%Y-%m-%d")
            self.current_time = dt.strftime("%H:%M")
        except ValueError:
            self.current_date = datetime.now().strftime("%Y-%m-%d")
            self.current_time = datetime.now().strftime("%H:%M")
        
        self._create_widgets(title, description)
    
    def _create_widgets(self, title: str, description: str):
        """Создание элементов интерфейса диалога."""
        # Заголовок
        tk.Label(self.root, text="Заголовок:", font=Styles.FONT_MAIN, bg=Styles.BG_WINDOW, fg=Styles.TEXT_DEFAULT).pack(pady=(Styles.PADDING_MEDIUM, 0), anchor=tk.W, padx=Styles.PADDING_MEDIUM)
        self.title_entry = tk.Entry(self.root, font=Styles.FONT_MAIN, width=Styles.INPUT_WIDTH_LONG, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT)
        self.title_entry.insert(0, title)
        self.title_entry.pack(pady=(0, Styles.PADDING_MEDIUM), padx=Styles.PADDING_MEDIUM, fill=tk.X)
        
        # Описание
        tk.Label(self.root, text="Описание:", font=Styles.FONT_MAIN, bg=Styles.BG_WINDOW, fg=Styles.TEXT_DEFAULT).pack(pady=(0, 0), anchor=tk.W, padx=Styles.PADDING_MEDIUM)
        self.desc_text = tk.Text(self.root, font=Styles.FONT_MAIN, width=Styles.INPUT_WIDTH_LONG, height=5, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT, wrap=tk.WORD)
        self.desc_text.insert("1.0", description)
        self.desc_text.pack(pady=(0, Styles.PADDING_MEDIUM), padx=Styles.PADDING_MEDIUM, fill=tk.X)
        
        # Дата
        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):", font=Styles.FONT_MAIN, bg=Styles.BG_WINDOW, fg=Styles.TEXT_DEFAULT).pack(pady=(0, 0), anchor=tk.W, padx=Styles.PADDING_MEDIUM)
        self.date_entry = tk.Entry(self.root, font=Styles.FONT_MAIN, width=20, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT)
        self.date_entry.insert(0, self.current_date)
        self.date_entry.pack(pady=(0, Styles.PADDING_MEDIUM), padx=Styles.PADDING_MEDIUM, fill=tk.X)
        
        # Время
        tk.Label(self.root, text="Время (ЧЧ:ММ):", font=Styles.FONT_MAIN, bg=Styles.BG_WINDOW, fg=Styles.TEXT_DEFAULT).pack(pady=(0, Styles.PADDING_MEDIUM), anchor=tk.W, padx=Styles.PADDING_MEDIUM)
        self.time_entry = tk.Entry(self.root, font=Styles.FONT_MAIN, width=10, bg=Styles.BG_ENTRY, fg=Styles.TEXT_DEFAULT, insertbackground=Styles.TEXT_DEFAULT)
        self.time_entry.insert(0, self.current_time)
        self.time_entry.pack(pady=(0, Styles.PADDING_LARGE), padx=Styles.PADDING_MEDIUM, fill=tk.X)
        
        # Кнопки
        btn_frame = tk.Frame(self.root, bg=Styles.BG_WINDOW)
        btn_frame.pack(pady=Styles.PADDING_MEDIUM)
        
        save_btn = tk.Button(btn_frame, text="Сохранить", command=self._save, font=Styles.FONT_MAIN, width=Styles.BUTTON_WIDTH, bg=Styles.BUTTON_ADD_BG, fg=Styles.BUTTON_FG)
        save_btn.pack(side=tk.LEFT, padx=Styles.PADDING_SMALL)
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=Styles.BUTTON_ADD_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=Styles.BUTTON_ADD_BG))
        
        cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.root.destroy, font=Styles.FONT_MAIN, width=Styles.BUTTON_WIDTH, bg=Styles.BUTTON_DELETE_BG, fg=Styles.BUTTON_FG)
        cancel_btn.pack(side=tk.LEFT, padx=Styles.PADDING_SMALL)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=Styles.BUTTON_DELETE_HOVER))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=Styles.BUTTON_DELETE_BG))
    
    def _save(self):
        """Обработчик кнопки сохранения."""
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        scheduled_at = f"{date_str} {time_str}:00"
        
        if not title:
            messagebox.showwarning("Внимание", "Заголовок обязателен!")
            return
        
        try:
            datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showwarning("Внимание", "Неверный формат даты!")
            return
        
        if self.callback:
            self.callback(self.reminder_id, title, description, scheduled_at)
        self.root.destroy()
