import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui import ToDoApp
import db


def main():
    try:
        app = QApplication(sys.argv)
        
        # Создаем таблицы базы данных
        try:
            db.create_tables()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка базы данных", 
                f"Не удалось создать таблицы базы данных:\n{str(e)}")
            return
        
        window = ToDoApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        error_msg = f"Произошла ошибка:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)  # Выводим в консоль для отладки
        QMessageBox.critical(None, "Критическая ошибка", error_msg)


if __name__ == "__main__":
    main()
