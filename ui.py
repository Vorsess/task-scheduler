from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLabel,
    QTabWidget,
    QDateTimeEdit,
    QSpacerItem,
    QSizePolicy,
    QFrame,
    QDialog,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QIcon
import qtawesome as qta
import db


class AddSubtaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить подзадачу")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.subtask_input = QLineEdit()
        self.subtask_input.setPlaceholderText("Введите подзадачу...")
        self.subtask_input.setMinimumHeight(40)
        layout.addWidget(self.subtask_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Умный планировщик задач")
        self.setGeometry(100, 100, 800, 800)

        # Изначальная тема - светлая
        self.is_dark_theme = False
        self.set_style(self.is_dark_theme)

        # Основной layout приложения
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        self.title_label = QLabel("Умный планировщик задач")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.layout.addWidget(self.title_label)

        # Ввод текста для добавления задач и кнопка создания
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите задачу...")
        self.task_input.setMinimumHeight(40)
        input_layout.addWidget(self.task_input)

        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDateTime(QDateTime.currentDateTime())
        self.deadline_input.setMinimumHeight(40)
        input_layout.addWidget(self.deadline_input)

        self.add_button = QPushButton()
        self.add_button.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.add_button.setText("Добавить")
        self.add_button.setMinimumHeight(40)
        self.add_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_button)

        self.layout.addWidget(input_container)

        # Поле для поиска задач
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 10, 10, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по задачам...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.search_tasks)
        search_layout.addWidget(self.search_input)

        self.layout.addWidget(search_container)

        # Добавляем вкладки для отображения задач
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.incomplete_tab = QWidget()
        self.complete_tab = QWidget()

        # Списки для невыполненных и выполненных задач
        self.incomplete_task_list = QListWidget()
        self.complete_task_list = QListWidget()

        # Устанавливаем layout для каждой вкладки
        incomplete_layout = QVBoxLayout()
        incomplete_layout.addWidget(self.incomplete_task_list)
        self.incomplete_tab.setLayout(incomplete_layout)

        complete_layout = QVBoxLayout()
        complete_layout.addWidget(self.complete_task_list)
        self.complete_tab.setLayout(complete_layout)

        # Добавляем вкладки в основной виджет вкладок
        self.tabs.addTab(self.incomplete_tab, qta.icon('fa5s.list', color='#2196F3'), "Активные задачи")
        self.tabs.addTab(self.complete_tab, qta.icon('fa5s.check-circle', color='#4CAF50'), "Выполненные задачи")
        self.layout.addWidget(self.tabs)

        # Кнопка переключения темы
        self.theme_button = QPushButton()
        self.theme_button.setIcon(qta.icon('fa5s.moon', color='white'))
        self.theme_button.setText("Сменить тему")
        self.theme_button.setMinimumHeight(40)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_button)

        # Настройка центрального виджета и компоновки
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Загрузка задач при запуске
        self.load_tasks()

        # Таймер для проверки дедлайнов
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_deadlines)
        self.notification_timer.start(60000)  # проверка каждые 60 секунд

    def set_style(self, dark):
        """Устанавливает стиль для приложения (темный или светлый)."""
        if dark:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1E1E1E;
                }
                QWidget {
                    color: #FFFFFF;
                }
                QFrame#inputContainer, QFrame#searchContainer {
                    background-color: #2D2D2D;
                    border-radius: 10px;
                }
                QLineEdit, QDateTimeEdit {
                    background-color: #3D3D3D;
                    color: #FFFFFF;
                    border: 2px solid #4D4D4D;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus, QDateTimeEdit:focus {
                    border: 2px solid #007ACC;
                }
                QPushButton {
                    background-color: #007ACC;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0098FF;
                }
                QListWidget {
                    background-color: #2D2D2D;
                    border: 2px solid #3D3D3D;
                    border-radius: 10px;
                    padding: 5px;
                }
                QListWidget::item {
                    background-color: #3D3D3D;
                    border-radius: 5px;
                    margin: 2px;
                    padding: 5px;
                }
                QListWidget::item:selected {
                    background-color: #007ACC;
                }
                QTabWidget::pane {
                    border: 2px solid #3D3D3D;
                    border-radius: 10px;
                }
                QTabBar::tab {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    padding: 8px 20px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #007ACC;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F5F5F5;
                }
                QWidget {
                    color: #000000;
                }
                QFrame#inputContainer, QFrame#searchContainer {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                    border: 1px solid #E0E0E0;
                }
                QLineEdit, QDateTimeEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 2px solid #E0E0E0;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus, QDateTimeEdit:focus {
                    border: 2px solid #2196F3;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QListWidget {
                    background-color: #FFFFFF;
                    border: 2px solid #E0E0E0;
                    border-radius: 10px;
                    padding: 5px;
                }
                QListWidget::item {
                    background-color: #F5F5F5;
                    border-radius: 5px;
                    margin: 2px;
                    padding: 5px;
                }
                QListWidget::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QTabWidget::pane {
                    border: 2px solid #E0E0E0;
                    border-radius: 10px;
                }
                QTabBar::tab {
                    background-color: #F5F5F5;
                    color: #000000;
                    padding: 8px 20px;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #2196F3;
                    color: white;
                }
            """)

    def toggle_theme(self):
        """Переключает тему (светлая/темная)."""
        self.is_dark_theme = not self.is_dark_theme
        self.set_style(self.is_dark_theme)
        if self.is_dark_theme:
            self.theme_button.setIcon(qta.icon('fa5s.sun', color='white'))
        else:
            self.theme_button.setIcon(qta.icon('fa5s.moon', color='white'))

    def load_tasks(self):
        """Загружает задачи из базы данных и отображает их в списке."""
        try:
            # Очищаем списки
        self.incomplete_task_list.clear()
        self.complete_task_list.clear()

            # Загружаем задачи
            tasks = db.load_tasks()
            
            for task_id, description, status, deadline in tasks:
                # Создаем виджет для задачи
                task_widget = QWidget()
                task_layout = QVBoxLayout(task_widget)
                task_layout.setSpacing(10)  # Увеличиваем отступ между элементами
                task_layout.setContentsMargins(10, 10, 10, 10)  # Увеличиваем отступы от краев
                
                # Создаем виджет для основной информации о задаче
                info_widget = QWidget()
                info_layout = QHBoxLayout(info_widget)
                info_layout.setContentsMargins(0, 0, 0, 0)
                
                # Добавляем описание задачи
                task_label = QLabel(description)
                task_label.setWordWrap(True)
                task_label.setStyleSheet("font-size: 14px;")  # Увеличиваем размер шрифта
                info_layout.addWidget(task_label, stretch=1)
                
                # Добавляем дедлайн, если он есть
                if deadline:
                    deadline_label = QLabel(f"Дедлайн: {deadline}")
                    deadline_label.setStyleSheet("color: #FF5722; font-size: 14px;")
                    info_layout.addWidget(deadline_label)
                
                task_layout.addWidget(info_widget)
                
                # Загружаем подзадачи
                subtasks = db.load_subtasks(task_id)
                if subtasks:
                    subtasks_widget = QWidget()
                    subtasks_layout = QVBoxLayout(subtasks_widget)
                    subtasks_layout.setSpacing(5)  # Отступ между подзадачами
                    subtasks_layout.setContentsMargins(20, 5, 0, 5)  # Отступы для подзадач
                    
                    for subtask_id, subtask_text, subtask_status in subtasks:
                        # Создаем виджет для подзадачи
                        subtask_widget = QWidget()
                        subtask_layout = QHBoxLayout(subtask_widget)
                        subtask_layout.setContentsMargins(0, 0, 0, 0)
                        subtask_layout.setSpacing(10)  # Отступ между текстом и кнопкой
                        
                        # Добавляем текст подзадачи
                        subtask_label = QLabel(f"• {subtask_text}")
                        subtask_label.setStyleSheet("font-size: 13px;")  # Размер шрифта подзадач
                        if subtask_status == 1:
                            subtask_label.setStyleSheet("color: #4CAF50; text-decoration: line-through; font-size: 13px;")
                        else:
                            subtask_label.setStyleSheet("color: #757575; font-size: 13px;")
                        subtask_layout.addWidget(subtask_label, stretch=1)
                        
                        # Добавляем кнопку для изменения статуса подзадачи
                        subtask_status_btn = QPushButton()
                        subtask_status_btn.setFixedSize(30, 30)  # Фиксированный размер кнопки
                        if subtask_status == 0:
                            subtask_status_btn.setIcon(qta.icon('fa5s.check', color='#4CAF50'))
                            subtask_status_btn.setToolTip("Отметить как выполненное")
                            subtask_status_btn.clicked.connect(
                                lambda checked, sid=subtask_id: self.complete_subtask(sid))
                        else:
                            subtask_status_btn.setIcon(qta.icon('fa5s.undo', color='#FFC107'))
                            subtask_status_btn.setToolTip("Отметить как невыполненное")
                            subtask_status_btn.clicked.connect(
                                lambda checked, sid=subtask_id: self.undo_subtask(sid))
                        subtask_layout.addWidget(subtask_status_btn)
                        
                        subtasks_layout.addWidget(subtask_widget)
                    
                    task_layout.addWidget(subtasks_widget)
                
                # Добавляем кнопки управления
                buttons_layout = self.add_task_buttons(task_widget, subtasks, status)
                task_layout.addLayout(buttons_layout)
                
                # Создаем элемент списка
                list_item = QListWidgetItem()
                list_item.setData(Qt.UserRole, task_id)
                
                # Устанавливаем размер элемента списка
                list_item.setSizeHint(task_widget.sizeHint())
                
                # Добавляем элемент в соответствующий список
                if status == 0:
                    self.incomplete_task_list.addItem(list_item)
                    self.incomplete_task_list.setItemWidget(list_item, task_widget)
                else:
                    self.complete_task_list.addItem(list_item)
                    self.complete_task_list.setItemWidget(list_item, task_widget)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить задачи: {str(e)}")

    def add_task_buttons(self, task_widget, subtasks, status):
        """Добавляет кнопки управления для задачи."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Увеличиваем отступ между кнопками

        # Кнопка для добавления подзадачи
        add_subtask_btn = QPushButton("Добавить подзадачу")
        add_subtask_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_subtask_btn.setMinimumHeight(35)  # Увеличиваем высоту кнопки
        add_subtask_btn.setStyleSheet("font-size: 13px;")  # Размер шрифта кнопки
        add_subtask_btn.clicked.connect(lambda: self.add_subtask(task_widget))
        button_layout.addWidget(add_subtask_btn)

        # Кнопка для изменения статуса задачи
        status_btn = QPushButton()
        status_btn.setMinimumHeight(35)  # Увеличиваем высоту кнопки
        status_btn.setStyleSheet("font-size: 13px;")  # Размер шрифта кнопки
        if status == 0:
            status_btn.setText("Выполнено")
            status_btn.setIcon(qta.icon('fa5s.check', color='white'))
            status_btn.clicked.connect(lambda: self.complete_task(task_widget))
        else:
            status_btn.setText("Не выполнено")
            status_btn.setIcon(qta.icon('fa5s.undo', color='white'))
            status_btn.clicked.connect(lambda: self.undo_task(task_widget))
        button_layout.addWidget(status_btn)

        # Кнопка для удаления задачи
        delete_btn = QPushButton("Удалить")
        delete_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        delete_btn.setMinimumHeight(35)  # Увеличиваем высоту кнопки
        delete_btn.setStyleSheet("font-size: 13px;")  # Размер шрифта кнопки
        delete_btn.clicked.connect(lambda: self.delete_task(task_widget))
        button_layout.addWidget(delete_btn)

        return button_layout

    def get_task_id_from_widget(self, task_widget):
        """Получает ID задачи из виджета."""
        # Находим элемент списка, содержащий этот виджет
        for list_widget in [self.incomplete_task_list, self.complete_task_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if list_widget.itemWidget(item) == task_widget:
                    return item.data(Qt.UserRole)
        return None

    def add_subtask(self, task_widget):
        """Добавляет подзадачу к выбранной задаче."""
        dialog = AddSubtaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_id = self.get_task_id_from_widget(task_widget)
            if task_id is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось определить ID задачи")
                return
                
            subtask_text = dialog.subtask_input.text().strip()
            if subtask_text:
                try:
                    db.add_subtask(task_id, subtask_text)
                    self.load_tasks()  # Перезагружаем список задач
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить подзадачу: {str(e)}")

    def complete_task(self, task_widget):
        """Отмечает задачу как выполненную."""
        task_id = self.get_task_id_from_widget(task_widget)
        if task_id is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось определить ID задачи")
            return
            
        try:
            db.update_task_status(task_id, 1)
        self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус задачи: {str(e)}")

    def undo_task(self, task_widget):
        """Отмечает задачу как невыполненную."""
        task_id = self.get_task_id_from_widget(task_widget)
        if task_id is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось определить ID задачи")
            return
            
        try:
            db.update_task_status(task_id, 0)
        self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус задачи: {str(e)}")

    def delete_task(self, task_widget):
        """Удаляет задачу."""
        task_id = self.get_task_id_from_widget(task_widget)
        if task_id is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось определить ID задачи")
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить эту задачу?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.delete_task(task_id)
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {str(e)}")

    def check_deadlines(self):
        """Проверка просроченных задач."""
        overdue_tasks = db.check_overdue_tasks(
            QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        )
        if overdue_tasks:
            QMessageBox.warning(
                self,
                "Просроченные задачи",
                f"Обнаружены просроченные задачи: {', '.join([task[0] for task in overdue_tasks])}",
            )

    def add_task(self):
        """Добавляет новую задачу в базу данных и обновляет список."""
        task_text = self.task_input.text().strip()
        deadline = self.deadline_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        if task_text:
            db.add_task(task_text, deadline)
            self.load_tasks()
            self.task_input.clear()
            self.deadline_input.setDateTime(QDateTime.currentDateTime())
        else:
            QMessageBox.warning(self, "Ошибка", "Задача не может быть пустой")

    def search_tasks(self):
        """Фильтрует задачи по тексту поиска."""
        search_term = self.search_input.text().lower()
        self.incomplete_task_list.clear()
        self.complete_task_list.clear()

        tasks = db.search_tasks(search_term)
        for row in tasks:
            task_id, description, status, deadline = row
            deadline_display = QDateTime.fromString(deadline, "yyyy-MM-dd HH:mm:ss")
            deadline_text = (
                deadline_display.toString("dd.MM.yyyy HH:mm")
                if deadline
                else "Без дедлайна"
            )

            task_item = QListWidgetItem(f"{description} (Дедлайн: {deadline_text})")
            task_item.setData(Qt.UserRole, task_id)

            # Загружаем подзадачи для каждой задачи
            sub_task_list = db.load_subtasks(task_id)

            # Выделяем просроченные задачи красным цветом
            if (
                deadline
                and QDateTime.currentDateTime() > deadline_display
                and status == 0
            ):
                task_item.setForeground(QColor("red"))

            self.add_task_buttons(task_item, sub_task_list, status)

    def complete_subtask(self, subtask_id):
        """Отмечает подзадачу как выполненную."""
        try:
            db.update_subtask_status(subtask_id, 1)
            self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус подзадачи: {str(e)}")

    def undo_subtask(self, subtask_id):
        """Отмечает подзадачу как невыполненную."""
        try:
            db.update_subtask_status(subtask_id, 0)
            self.load_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус подзадачи: {str(e)}")
