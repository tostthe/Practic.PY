"""
Панель управления приложением

Содержит элементы управления для загрузки изображений,
работы с камерой, выбора RGB каналов и функций обработки.
"""
import torch
import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QComboBox, QLabel, QSlider, QSpinBox,
    QCheckBox, QFrame, QScrollArea, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ControlPanel(QWidget):
    """Панель управления приложением"""
    
    # Сигналы
    load_image_requested = pyqtSignal()
    camera_toggle_requested = pyqtSignal()
    capture_frame_requested = pyqtSignal()
    channel_changed = pyqtSignal(str)
    processing_requested = pyqtSignal(str, dict)  # function_name, parameters
    save_image_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.current_image = None
        self.camera_active = False
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        
        # Основной layout с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        main_layout = QVBoxLayout()
        scroll_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_widget)
        
        # Главный layout панели
        panel_layout = QVBoxLayout()
        panel_layout.addWidget(scroll_area)
        self.setLayout(panel_layout)
        
        # Заголовок
        title_label = QLabel("🎛️ Панель управления")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Группы элементов управления
        main_layout.addWidget(self.create_file_group())
        main_layout.addWidget(self.create_camera_group())
        main_layout.addWidget(self.create_channel_group())
        main_layout.addWidget(self.create_variant_functions_group())
        main_layout.addWidget(self.create_info_group())
        
        # Растягивающий элемент
        main_layout.addStretch()
        
        # Установка фиксированной ширины
        self.setMaximumWidth(350)
        self.setMinimumWidth(300)
    
    def create_file_group(self):
        """Создание группы работы с файлами"""
        
        group = QGroupBox("📁 Файлы")
        layout = QVBoxLayout()
        
        # Кнопка загрузки изображения
        load_btn = QPushButton("📂 Загрузить изображение")
        load_btn.clicked.connect(self.load_image_requested.emit)
        layout.addWidget(load_btn)

        # Кнопка сохранения изображения
        save_btn = QPushButton("💾 Сохранить изображение")
        save_btn.clicked.connect(self.save_image_requested.emit)
        layout.addWidget(save_btn)
        
        # Информация о файле
        self.file_info_label = QLabel("Файл не выбран")
        self.file_info_label.setStyleSheet("color: #666; font-size: 11px;")
        self.file_info_label.setWordWrap(True)
        layout.addWidget(self.file_info_label)
        
        group.setLayout(layout)
        return group
    
    def create_camera_group(self):
        """Создание группы работы с камерой"""
        
        group = QGroupBox("📷 Веб-камера")
        layout = QVBoxLayout()
        
        # Кнопка включения/выключения камеры
        self.camera_btn = QPushButton("📷 Включить камеру")
        self.camera_btn.clicked.connect(self.toggle_camera)
        layout.addWidget(self.camera_btn)
        
        # Кнопка захвата кадра
        self.capture_btn = QPushButton("📸 Захватить кадр")
        self.capture_btn.clicked.connect(self.capture_frame_requested.emit)
        self.capture_btn.setEnabled(False)
        layout.addWidget(self.capture_btn)
        
        # Статус камеры
        self.camera_status_label = QLabel("Камера выключена")
        self.camera_status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.camera_status_label)
        
        group.setLayout(layout)
        return group
    
    def create_channel_group(self):
        """Создание группы выбора RGB каналов"""
        
        group = QGroupBox("🎨 RGB каналы")
        layout = QVBoxLayout()
        
        # Комбо-бокс выбора канала
        self.channel_combo = QComboBox()
        self.channel_combo.addItems([
            "RGB (оригинал)",
            "Красный канал", 
            "Зеленый канал",
            "Синий канал"
        ])
        self.channel_combo.currentTextChanged.connect(self.on_channel_changed)
        layout.addWidget(self.channel_combo)
        
        # Информация о канале
        self.channel_info_label = QLabel("Отображается оригинальное изображение")
        self.channel_info_label.setStyleSheet("color: #666; font-size: 11px;")
        self.channel_info_label.setWordWrap(True)
        layout.addWidget(self.channel_info_label)
        
        group.setLayout(layout)
        return group
    
    def create_variant_functions_group(self):
        """Создание группы функций варианта"""
        
        group = QGroupBox("⚙️ Функции варианта")
        layout = QVBoxLayout()
        
        # Функция 1: Изменение размера
        resize_btn = QPushButton("📏 Изменить размер")
        resize_btn.clicked.connect(self.resize_image_dialog)
        layout.addWidget(resize_btn)
        
        # Функция 8: Понижение яркости
        brightness_btn = QPushButton("🔅 Понизить яркость")
        brightness_btn.clicked.connect(self.decrease_brightness_dialog)
        layout.addWidget(brightness_btn)
        
        # Функция 13: Рисование синего прямоугольника
        rect_btn = QPushButton("🔷 Нарисовать синий прямоугольник")
        rect_btn.clicked.connect(self.draw_blue_rectangle_dialog)
        layout.addWidget(rect_btn)
        
        # Поворот изображения
        rotate_btn = QPushButton("🔄 Повернуть изображение")
        rotate_btn.clicked.connect(self.rotate_image_dialog)
        layout.addWidget(rotate_btn)
        
        # Размытие изображения
        blur_btn = QPushButton("🌫️ Размыть изображение")
        blur_btn.clicked.connect(self.apply_blur_dialog)
        layout.addWidget(blur_btn)
        
        # Обрезка изображения
        crop_btn = QPushButton("✂️ Обрезать изображение")
        crop_btn.clicked.connect(self.crop_image_dialog)
        layout.addWidget(crop_btn)
        
        # Добавление черной рамки
        border_btn = QPushButton("⬛ Добавить рамки")
        border_btn.clicked.connect(self.add_border_dialog)
        layout.addWidget(border_btn)
        
        # Кнопка сброса
        reset_btn = QPushButton("🔄 Сбросить изменения")
        reset_btn.clicked.connect(self.reset_processing)
        layout.addWidget(reset_btn)
        
        # Включение/выключение кнопок при наличии изображения
        self.processing_buttons = [resize_btn, brightness_btn, rect_btn, rotate_btn, 
                                  blur_btn, crop_btn, border_btn, reset_btn]
        for btn in self.processing_buttons:
            btn.setEnabled(False)
        
        group.setLayout(layout)
        return group
    
    def create_info_group(self):
        """Создание группы информации"""
        
        group = QGroupBox("ℹ️ Информация")
        layout = QVBoxLayout()
        
        # Информация о библиотеках
        try:
            opencv_version = cv2.__version__
        except ImportError:
            opencv_version = "не установлен"
        
        try:
            pytorch_version = torch.__version__
        except ImportError:
            pytorch_version = "не установлен"
        
        versions_text = f"""
        📷 OpenCV: {opencv_version}
        🔥 PyTorch: {pytorch_version}
        """
        
        versions_label = QLabel(versions_text.strip())
        versions_label.setStyleSheet("font-size: 10px; color: #555;")
        layout.addWidget(versions_label)
        
        group.setLayout(layout)
        return group
    
    def toggle_camera(self):
        """Переключение состояния камеры"""
        
        self.camera_toggle_requested.emit()
    
    def on_channel_changed(self, channel_text):
        """Обработка изменения RGB канала"""
        
        # Определение типа канала
        if "оригинал" in channel_text.lower():
            channel = "original"
            info_text = "Отображается оригинальное изображение"
        elif "красный" in channel_text.lower():
            channel = "red"
            info_text = "Отображается только красный канал"
        elif "зеленый" in channel_text.lower():
            channel = "green"
            info_text = "Отображается только зеленый канал"
        elif "синий" in channel_text.lower():
            channel = "blue"
            info_text = "Отображается только синий канал"
        else:
            channel = "original"
            info_text = "Неизвестный канал"
        
        # Обновление информации
        self.channel_info_label.setText(info_text)
        
        # Испускание сигнала
        self.channel_changed.emit(channel)
    
    def resize_image_dialog(self):
        """Диалог изменения размера изображения"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        # Получение текущих размеров
        height, width = self.current_image.shape[:2]
        
        # Диалог ввода новой ширины
        new_width, ok1 = QInputDialog.getInt(
            self, "Изменение размера", 
            f"Текущая ширина: {width}\nВведите новую ширину:",
            width, 1, 8000
        )
        
        if not ok1:
            return
        
        # Диалог ввода новой высоты
        new_height, ok2 = QInputDialog.getInt(
            self, "Изменение размера", 
            f"Текущая высота: {height}\nВведите новую высоту:",
            height, 1, 8000
        )
        
        if not ok2:
            return
        
        # Запрос обработки
        parameters = {
            'new_width': new_width,
            'new_height': new_height
        }
        self.processing_requested.emit('resize_image', parameters)
    
    def decrease_brightness_dialog(self):
        """Диалог понижения яркости"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        # Диалог ввода значения
        value, ok = QInputDialog.getInt(
            self, "Понижение яркости", 
            "Введите значение для понижения яркости (0-100):",
            20, 0, 100
        )
        
        if not ok:
            return
        
        # Запрос обработки
        parameters = {
            'value': value
        }
        self.processing_requested.emit('decrease_brightness', parameters)
    
    def draw_blue_rectangle_dialog(self):
        """Диалог рисования синего прямоугольника"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        height, width = self.current_image.shape[:2]
        
        # Диалог ввода координат верхнего левого угла
        top_left_x, ok1 = QInputDialog.getInt(
            self, "Рисование прямоугольника", 
            f"Размер изображения: {width}×{height}\nВведите X координату верхнего левого угла:",
            0, 0, width - 1
        )
        
        if not ok1:
            return
        
        top_left_y, ok2 = QInputDialog.getInt(
            self, "Рисование прямоугольника", 
            f"Введите Y координату верхнего левого угла:",
            0, 0, height - 1
        )
        
        if not ok2:
            return
        
        # Диалог ввода ширины
        rect_width, ok3 = QInputDialog.getInt(
            self, "Рисование прямоугольника", 
            f"Введите ширину прямоугольника:",
            100, 1, width - top_left_x
        )
        
        if not ok3:
            return
        
        # Диалог ввода высоты
        rect_height, ok4 = QInputDialog.getInt(
            self, "Рисование прямоугольника", 
            f"Введите высоту прямоугольника:",
            100, 1, height - top_left_y
        )
        
        if not ok4:
            return
        
        # Запрос обработки
        parameters = {
            'top_left_x': top_left_x,
            'top_left_y': top_left_y,
            'width': rect_width,
            'height': rect_height
        }
        self.processing_requested.emit('draw_blue_rectangle', parameters)
    
    def rotate_image_dialog(self):
        """Диалог поворота изображения"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        # Диалог ввода угла
        angle, ok = QInputDialog.getInt(
            self, "Поворот изображения", 
            "Введите угол поворота (в градусах):",
            0, -360, 360
        )
        
        if not ok:
            return
        
        # Запрос обработки
        parameters = {
            'angle': angle
        }
        self.processing_requested.emit('rotate_image', parameters)
    
    def apply_blur_dialog(self):
        """Диалог размытия изображения"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        # Диалог ввода размера ядра
        kernel_size, ok = QInputDialog.getInt(
            self, "Размытие изображения", 
            "Введите размер ядра (нечетное число):",
            5, 3, 31, 2  
        )
        
        if not ok:
            return
        
        if kernel_size % 2 == 0:
            kernel_size += 1
            QMessageBox.information(self, "Корректировка", 
                                  f"Размер ядра изменен на {kernel_size} (должен быть нечетным)")
        
        # Запрос обработки
        parameters = {
            'kernel_size': kernel_size
        }
        self.processing_requested.emit('apply_blur', parameters)
    
    def crop_image_dialog(self):
        """Диалог обрезки изображения"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        height, width = self.current_image.shape[:2]
        
        # Диалог ввода X координаты
        x, ok1 = QInputDialog.getInt(
            self, "Обрезка изображения", 
            f"Размер изображения: {width}×{height}\nВведите X координату верхнего левого угла:",
            0, 0, width - 1
        )
        
        if not ok1:
            return
        
        # Диалог ввода Y координаты
        y, ok2 = QInputDialog.getInt(
            self, "Обрезка изображения", 
            f"Введите Y координату верхнего левого угла:",
            0, 0, height - 1
        )
        
        if not ok2:
            return
        
        # Диалог ввода ширины
        w, ok3 = QInputDialog.getInt(
            self, "Обрезка изображения", 
            f"Введите ширину области:",
            min(100, width - x), 1, width - x
        )
        
        if not ok3:
            return
        
        # Диалог ввода высоты
        h, ok4 = QInputDialog.getInt(
            self, "Обрезка изображения", 
            f"Введите высоту области:",
            min(100, height - y), 1, height - y
        )
        
        if not ok4:
            return
        
        # Запрос обработки
        parameters = {
            'x': x,
            'y': y,
            'width': w,
            'height': h
        }
        self.processing_requested.emit('crop_image', parameters)
    
    def add_border_dialog(self):
        """Диалог добавления черной рамки"""
        
        if self.current_image is None:
            QMessageBox.warning(self, "Предупреждение", 
                              "Сначала загрузите изображение")
            return
        
        # Диалоги ввода для каждой стороны
        top, ok1 = QInputDialog.getInt(
            self, "Черная рамка", 
            "Верхняя граница (пиксели):",
            10, 0, 500
        )
        if not ok1: return
        
        bottom, ok2 = QInputDialog.getInt(
            self, "Черная рамка", 
            "Нижняя граница (пиксели):",
            10, 0, 500
        )
        if not ok2: return
        
        left, ok3 = QInputDialog.getInt(
            self, "Черная рамка", 
            "Левая граница (пиксели):",
            10, 0, 500
        )
        if not ok3: return
        
        right, ok4 = QInputDialog.getInt(
            self, "Черная рамка", 
            "Правая граница (пиксели):",
            10, 0, 500
        )
        if not ok4: return
        
        # Запрос обработки
        parameters = {
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right
        }
        self.processing_requested.emit('add_black_border', parameters)
    
    def reset_processing(self):
        """Сброс обработки к оригинальному изображению"""
        
        if self.current_image is None:
            return
        
        # Сброс канала к оригиналу
        self.channel_combo.setCurrentIndex(0)
        
        # Запрос сброса в главном окне (через сигналы)
        self.processing_requested.emit('reset', {})
    
    def on_image_loaded(self, image):
        """Слот для обработки загрузки нового изображения"""
        
        self.current_image = image
    
        if image is not None:
            # Включение кнопок обработки
            for btn in self.processing_buttons:
                btn.setEnabled(True)
            
            # Обновление информации о файле
            height, width = image.shape[:2]
            channels = len(image.shape)
            
            info_text = f"Размер: {width}×{height}\n"
            if channels == 3:
                info_text += "Формат: Цветное (BGR)"
            else:
                info_text += "Формат: Оттенки серого"
            
            self.file_info_label.setText(info_text)
            
            # Сброс обработанного изображения
            self.parent().processed_image = None
        else:
            # Выключение кнопок обработки
            for btn in self.processing_buttons:
                btn.setEnabled(False)
            
            self.file_info_label.setText("Файл не выбран")
    
    def on_camera_started(self):
        """Слот для обработки запуска камеры"""
        
        self.camera_active = True
        self.camera_btn.setText("📷 Выключить камеру")
        self.capture_btn.setEnabled(True)
        self.camera_status_label.setText("Камера активна")
        self.camera_status_label.setStyleSheet("color: green; font-size: 11px;")
    
    def on_camera_stopped(self):
        """Слот для обработки остановки камеры"""
        
        self.camera_active = False
        self.camera_btn.setText("📷 Включить камеру")
        self.capture_btn.setEnabled(False)
        self.camera_status_label.setText("Камера выключена")
        self.camera_status_label.setStyleSheet("color: #666; font-size: 11px;")
    
    def reset_controls(self):
        """Сброс элементов управления к начальному состоянию"""
        
        # Сброс канала
        self.channel_combo.setCurrentIndex(0)
        
        # Сброс информации о канале
        self.channel_info_label.setText("Отображается оригинальное изображение")
