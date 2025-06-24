"""
Главное окно приложения обработки изображений

Содержит основной интерфейс пользователя и координирует
работу всех компонентов приложения.
"""

import os
import logging
import numpy as np 
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QHBoxLayout, QWidget, QMenuBar,
    QAction, QStatusBar, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from .image_viewer import ImageViewer
from .control_panel import ControlPanel
from processing.image_processor import ImageProcessor
from camera.camera_manager import CameraManager
from utils.file_handler import FileHandler
from utils.error_handler import ErrorHandler
from configs.settings import AppSettings

class ImageProcessorWindow(QMainWindow):
    """Главное окно приложения"""
    
    # Сигналы
    image_loaded = pyqtSignal(object)
    processing_finished = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        
        # Инициализация компонентов
        self.current_image = None
        self.processed_image = None
        self.camera_manager = None
        
        # Инициализация сервисов
        self.image_processor = ImageProcessor()
        self.file_handler = FileHandler()
        self.error_handler = ErrorHandler()
        self.settings = AppSettings()
        
        # Настройки
        self.camera_active = False
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
        # Инициализация интерфейса
        self.init_ui()
        self.setup_connections()
        
        self.logger.info("Главное окно инициализировано")
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        
        # Настройка окна
        self.setWindowTitle("🖼️ Обработка изображений - Ознакомительная практика")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Создание меню
        self.create_menu_bar()
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout с разделителем
        splitter = QSplitter(Qt.Horizontal)
        central_widget_layout = QHBoxLayout()
        central_widget_layout.addWidget(splitter)
        central_widget.setLayout(central_widget_layout)
        
        # Создание компонентов интерфейса
        self.image_viewer = ImageViewer()
        self.control_panel = ControlPanel()
        
        # Добавление в splitter
        splitter.addWidget(self.image_viewer)
        splitter.addWidget(self.control_panel)
        splitter.setSizes([1000, 400])  # Пропорции 70/30
        
        # Строка состояния
        self.create_status_bar()
        
        # Применение стилей
        self.apply_styles()
    
    def create_menu_bar(self):
        """Создание меню"""
        
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        open_action = QAction('Открыть изображение', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_image)
        file_menu.addAction(open_action)
        
        save_action = QAction('Сохранить результат', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Камера"
        camera_menu = menubar.addMenu('Камера')
        
        start_camera_action = QAction('Включить камеру', self)
        start_camera_action.triggered.connect(self.start_camera)
        camera_menu.addAction(start_camera_action)
        
        stop_camera_action = QAction('Выключить камеру', self)
        stop_camera_action.triggered.connect(self.stop_camera)
        camera_menu.addAction(stop_camera_action)
        
        capture_action = QAction('Захватить кадр', self)
        capture_action.setShortcut('Space')
        capture_action.triggered.connect(self.capture_frame)
        camera_menu.addAction(capture_action)
        
        # Меню "Обработка"
        processing_menu = menubar.addMenu('Обработка')
        
        reset_action = QAction('Сбросить изменения', self)
        reset_action.setShortcut('Ctrl+R')
        reset_action.triggered.connect(self.reset_image)
        processing_menu.addAction(reset_action)
        
        # Добавляем разделитель
        processing_menu.addSeparator()
        
        # Новый пункт: Поворот изображения
        rotate_action = QAction('Повернуть изображение', self)
        rotate_action.triggered.connect(self.show_rotate_dialog)
        processing_menu.addAction(rotate_action)
        
        # Новый пункт: Размытие изображения
        blur_action = QAction('Размыть изображение', self)
        blur_action.triggered.connect(self.show_blur_dialog)
        processing_menu.addAction(blur_action)
        
        # Новый пункт: Обрезка изображения
        crop_action = QAction('Обрезать изображение', self)
        crop_action.triggered.connect(self.show_crop_dialog)
        processing_menu.addAction(crop_action)
        
        # Новый пункт: Добавить черную рамку
        border_action = QAction('Добавить черную рамку', self)
        border_action.triggered.connect(self.show_border_dialog)
        processing_menu.addAction(border_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def apply_styles(self):
        """Применение стилей к интерфейсу"""
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #e1e1e1;
                border-bottom: 1px solid #c0c0c0;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #d0d0d0;
            }
            QStatusBar {
                background-color: #e1e1e1;
                border-top: 1px solid #c0c0c0;
            }
        """)
    
    def setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        
        # Соединения с панелью управления
        self.control_panel.load_image_requested.connect(self.load_image)
        self.control_panel.camera_toggle_requested.connect(self.toggle_camera)
        self.control_panel.capture_frame_requested.connect(self.capture_frame)
        self.control_panel.channel_changed.connect(self.change_channel)
        self.control_panel.processing_requested.connect(self.process_image)
        self.control_panel.save_image_requested.connect(self.save_image)
        
        # Соединения с обработчиком изображений
        self.image_loaded.connect(self.control_panel.on_image_loaded)
        self.processing_finished.connect(self.image_viewer.update_image)
    
    def load_image(self):
        """Загрузка изображения из файла"""
        
        try:
            file_path = self.file_handler.open_file_dialog(self)
            if file_path:
                self.current_image = self.file_handler.load_image(file_path)
                
                if self.current_image is not None:
                    self.image_viewer.set_image(self.current_image)
                    self.image_loaded.emit(self.current_image)
                    
                    # Обновление статуса
                    file_name = Path(file_path).name
                    height, width = self.current_image.shape[:2]
                    self.status_bar.showMessage(
                        f"Загружено: {file_name} ({width}×{height})"
                    )
                    
                    self.logger.info(f"Изображение загружено: {file_path}")
                else:
                    raise ValueError("Не удалось загрузить изображение")
                    
        except Exception as e:
            self.handle_error(f"Ошибка загрузки изображения: {str(e)}")
    
    def save_image(self):
        """Сохранение обработанного изображения"""
        
        try:
            # Используем обработанное изображение, если оно есть, иначе оригинальное
            image_to_save = self.processed_image if self.processed_image is not None else self.current_image
            
            if image_to_save is None:
                QMessageBox.warning(self, "Предупреждение", 
                                  "Нет изображения для сохранения")
                return
            
            file_path = self.file_handler.save_file_dialog(self)
            if file_path:
                success = self.file_handler.save_image(image_to_save, file_path)
                if success:
                    self.status_bar.showMessage(f"Сохранено: {Path(file_path).name}")
                    self.logger.info(f"Изображение сохранено: {file_path}")
                else:
                    raise RuntimeError("Не удалось сохранить изображение")
                
        except Exception as e:
            self.handle_error(f"Ошибка сохранения: {str(e)}")
    
    def start_camera(self):
        """Запуск камеры"""
        
        try:
            if not self.camera_manager:
                self.camera_manager = CameraManager()
                self.camera_manager.frame_ready.connect(self.image_viewer.set_image)
                self.camera_manager.error_occurred.connect(self.handle_camera_error)
                self.camera_manager.camera_started.connect(self.on_camera_started)
                self.camera_manager.camera_stopped.connect(self.on_camera_stopped)
            
            self.camera_manager.start_capture()
            self.camera_active = True
            self.status_bar.showMessage("Камера активна")
            self.logger.info("Камера запущена")
            
        except Exception as e:
            self.handle_error(f"Ошибка запуска камеры: {str(e)}")

    def on_camera_started(self):
        """Обработка сигнала запуска камеры"""

        self.control_panel.on_camera_started()
        self.camera_active = True
    
    def on_camera_stopped(self):
        """Обработка сигнала остановки камеры"""
        
        self.control_panel.on_camera_stopped()
        self.camera_active = False
    
    def stop_camera(self):
        """Остановка камеры"""
        
        try:
            if self.camera_manager:
                self.camera_manager.stop_capture()
            
            self.camera_active = False
            self.status_bar.showMessage("Камера выключена")
            self.logger.info("Камера остановлена")
            
        except Exception as e:
            self.handle_error(f"Ошибка остановки камеры: {str(e)}")
    
    def toggle_camera(self):
        """Переключение состояния камеры"""
        
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()
    
    def capture_frame(self):
        """Захват кадра с камеры"""
        
        try:
            if self.camera_manager and self.camera_active:
                frame = self.camera_manager.capture_single_frame()
                if frame is not None:
                    self.current_image = frame.copy()
                    self.image_viewer.set_image(self.current_image)
                    self.image_loaded.emit(self.current_image)
                    self.status_bar.showMessage("Кадр захвачен")
                    self.logger.info("Кадр захвачен с камеры")
                else:
                    QMessageBox.warning(self, "Предупреждение", 
                                      "Не удалось захватить кадр")
            else:
                QMessageBox.warning(self, "Предупреждение", 
                                  "Камера не активна")
                
        except Exception as e:
            self.handle_error(f"Ошибка захвата кадра: {str(e)}")
    
    def change_channel(self, channel):
        """Изменение RGB канала"""

        try:
            # Берем текущее изображение (обработанное или оригинальное)
            current_img = self.processed_image if self.processed_image is not None else self.current_image
            
            if current_img is None:
                return
            
            # Создаем изображение только для отображения
            display_image = self.image_processor.create_channel_display(current_img, channel)
            self.image_viewer.set_image(display_image)
            
            self.status_bar.showMessage(f"Отображается: {channel}")
            
        except Exception as e:
            self.handle_error(f"Ошибка обработки канала: {str(e)}")
        
    def process_image(self, function_name, parameters):
        """Обработка изображения заданной функцией"""

        try:
            # Для сброса используем оригинальное изображение
            if function_name == 'reset':
                current_img = self.current_image
            else:
                # Берем текущее изображение (обработанное или оригинальное)
                current_img = self.processed_image if self.processed_image is not None else self.current_image
            
            if current_img is None:
                QMessageBox.warning(self, "Предупреждение", 
                                "Загрузите изображение для обработки")
                return
            
            # Для сброса просто используем оригинал
            if function_name == 'reset':
                self.processed_image = None
                self.image_viewer.set_image(self.current_image)
                self.status_bar.showMessage("Изменения сброшены")
                self.control_panel.reset_controls()
                return
            
            # Получение функции обработки
            process_function = getattr(self.image_processor, function_name, None)
            if process_function is None:
                raise ValueError(f"Функция {function_name} не найдена")
            
            # Выполнение обработки
            self.processed_image = process_function(current_img, **parameters)
            self.image_viewer.set_image(self.processed_image)
            self.processing_finished.emit(self.processed_image)
            
            self.status_bar.showMessage(f"Применена обработка: {function_name}")
            self.logger.info(f"Обработка выполнена: {function_name}")
            
        except Exception as e:
            self.handle_error(f"Ошибка обработки: {str(e)}")
    
    def reset_image(self):
        """Сброс изменений к оригинальному изображению"""
        
        if self.current_image is not None:
            self.processed_image = None
            self.image_viewer.set_image(self.current_image)
            self.status_bar.showMessage("Изменения сброшены")
            self.control_panel.reset_controls()
    
    def handle_error(self, error_message):
        """Обработка ошибок"""
        
        self.logger.error(error_message)
        QMessageBox.critical(self, "Ошибка", error_message)
        self.status_bar.showMessage("Ошибка выполнения операции")
    
    def handle_camera_error(self, error_message):
        """Обработка ошибок камеры"""
        
        self.logger.error(f"Ошибка камеры: {error_message}")
        QMessageBox.warning(self, "Ошибка камеры", error_message)
        self.camera_active = False
        self.status_bar.showMessage("Ошибка камеры")
    
    def show_rotate_dialog(self):
        """Показать диалог поворота изображения"""
        self.control_panel.rotate_image_dialog()
    
    def show_blur_dialog(self):
        """Показать диалог размытия изображения"""
        self.control_panel.apply_blur_dialog()
    
    def show_crop_dialog(self):
        """Показать диалог обрезки изображения"""
        self.control_panel.crop_image_dialog()
    
    def show_border_dialog(self):
        """Показать диалог добавления черной рамки"""
        self.control_panel.add_border_dialog()
    
    def show_about(self):
        """Отображение информации о программе"""
        
        about_text = """
        <h3>Обработка изображений</h3>
        <p><b>Версия:</b> 1.0</p>
        <p><b>Автор:</b> Илья Попов Евгеньевич</p>
        <p><b>Группа:</b> ЗКИ24-16Б</p>
        <p><b>Вариант:</b> 17 Выриант</p>
        <br>
        <p>Приложение для ознакомительной практики по программной инженерии.</p>
        <p>Включает работу с изображениями, RGB каналами и веб-камерой.</p>
        """
        
        QMessageBox.about(self, "О программе", about_text)
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        
        # Остановка камеры при закрытии
        if self.camera_active:
            self.stop_camera()
        
        self.logger.info("Приложение закрыто")
        event.accept()
