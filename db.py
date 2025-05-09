import sqlite3
from datetime import datetime
import os
import traceback

# Создаем и подключаемся к базе данных SQLite
DB_FILE = "tasks.db"

def get_connection():
    """Создает и возвращает соединение с базой данных."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")  # Включаем поддержку внешних ключей
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {str(e)}")
        raise

def create_tables():
    """Создает таблицы в базе данных, если они не существуют."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Проверяем существование временной таблицы и удаляем её, если она существует
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks_new'")
        if c.fetchone():
            print("Удаление временной таблицы tasks_new...")
            c.execute("DROP TABLE tasks_new")
        
        # Проверяем существование таблицы tasks
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        tasks_exists = c.fetchone() is not None
        
        if not tasks_exists:
            print("Создание таблицы tasks...")
            c.execute("""
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status INTEGER DEFAULT 0,
                    deadline TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            # Проверяем существование колонки created_at
            c.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'created_at' not in columns:
                print("Обновление структуры таблицы tasks...")
                # Создаем временную таблицу с новой структурой
                c.execute("""
                    CREATE TABLE tasks_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        status INTEGER DEFAULT 0,
                        deadline TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Копируем данные из старой таблицы
                c.execute("""
                    INSERT INTO tasks_new (id, description, status, deadline)
                    SELECT id, description, status, deadline FROM tasks
                """)
                
                # Удаляем старую таблицу
                c.execute("DROP TABLE tasks")
                
                # Переименовываем новую таблицу
                c.execute("ALTER TABLE tasks_new RENAME TO tasks")
                print("Структура таблицы tasks обновлена")
        
        # Проверяем существование таблицы sub_tasks
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sub_tasks'")
        sub_tasks_exists = c.fetchone() is not None
        
        if not sub_tasks_exists:
            print("Создание таблицы sub_tasks...")
            c.execute("""
                CREATE TABLE sub_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    description TEXT NOT NULL,
                    status INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
        else:
            # Проверяем существование колонки status в таблице sub_tasks
            c.execute("PRAGMA table_info(sub_tasks)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'status' not in columns:
                print("Обновление структуры таблицы sub_tasks...")
                # Создаем временную таблицу с новой структурой
                c.execute("""
                    CREATE TABLE sub_tasks_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id INTEGER,
                        description TEXT NOT NULL,
                        status INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                    )
                """)
                
                # Копируем данные из старой таблицы
                c.execute("""
                    INSERT INTO sub_tasks_new (id, task_id, description, created_at)
                    SELECT id, task_id, description, created_at FROM sub_tasks
                """)
                
                # Удаляем старую таблицу
                c.execute("DROP TABLE sub_tasks")
                
                # Переименовываем новую таблицу
                c.execute("ALTER TABLE sub_tasks_new RENAME TO sub_tasks")
                print("Структура таблицы sub_tasks обновлена")
        
        conn.commit()
        print("Таблицы успешно созданы/обновлены")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {str(e)}")
        print(traceback.format_exc())
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_task(description, deadline):
    """Добавляет новую задачу в базу данных."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO tasks (description, status, deadline) VALUES (?, ?, ?)",
            (description, 0, deadline)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении задачи: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def update_task_status(task_id, status):
    """Обновляет статус задачи (выполнена/не выполнена)."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении статуса задачи: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def delete_task(task_id):
    """Удаляет задачу и все её подзадачи из базы данных."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении задачи: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def load_tasks():
    """Загружает все задачи из базы данных."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, description, status, deadline 
            FROM tasks 
            ORDER BY created_at DESC
        """)
        tasks = c.fetchall()
        return tasks
    except Exception as e:
        print(f"Ошибка при загрузке задач: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def load_subtasks(task_id):
    """Загружает подзадачи для заданной задачи."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, description, status 
            FROM sub_tasks 
            WHERE task_id = ? 
            ORDER BY created_at ASC
        """, (task_id,))
        subtasks = c.fetchall()
        return subtasks
    except Exception as e:
        print(f"Ошибка при загрузке подзадач: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def add_subtask(task_id, description):
    """Добавляет подзадачу для указанной задачи."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO sub_tasks (task_id, description) VALUES (?, ?)",
            (task_id, description)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении подзадачи: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def check_overdue_tasks(now):
    """Проверяет задачи, у которых истек срок дедлайна."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT description 
            FROM tasks 
            WHERE deadline < ? AND status = 0
        """, (now,))
        tasks = c.fetchall()
        return tasks
    except Exception as e:
        print(f"Ошибка при проверке просроченных задач: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def search_tasks(search_term):
    """Поиск задач по тексту."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        search_pattern = f"%{search_term}%"
        c.execute("""
            SELECT id, description, status, deadline 
            FROM tasks 
            WHERE description LIKE ? 
            ORDER BY created_at DESC
        """, (search_pattern,))
        tasks = c.fetchall()
        return tasks
    except Exception as e:
        print(f"Ошибка при поиске задач: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def update_subtask_status(subtask_id, status):
    """Обновляет статус подзадачи."""
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE sub_tasks SET status = ? WHERE id = ?", (status, subtask_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении статуса подзадачи: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
