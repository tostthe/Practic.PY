"""
Виджет для отображения изображений

Обеспечивает просмотр изображений с возможностью
масштабирования и прокрутки.
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, 
    QHBoxLayout, QPushButton, QSlider, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont

class ImageViewer(QWidget):
    """Виджет для отображения изображений"""
    
    # Сигналы
    image_clicked = pyqtSignal(int, int)
    zoom_changed = pyqtSignal(float)
    crop_applied = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        
        self.current_image = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.crop_mode = False
        self.crop_start = None
        self.crop_end = None
        self.crop_rect = None
        self.dragging = False
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        
        # Основной layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title_label = QLabel("📷 Просмотр изображения")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Область прокрутки для изображения
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setMinimumSize(600, 400)
        
        # Label для отображения изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                background-color: #fafafa;
                border-radius: 5px;
                min-height: 300px;
                color: #666;
                font-size: 14px;
            }
        """)
        self.image_label.setText("📁 Загрузите изображение\nили включите камеру")
        self.image_label.mousePressEvent = self.on_image_click
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        
        # Панель управления масштабом
        zoom_panel = self.create_zoom_panel()
        layout.addWidget(zoom_panel)
        
        # Панель информации
        info_panel = self.create_info_panel()
        layout.addWidget(info_panel)
    
    def create_zoom_panel(self):
        """Создание панели управления масштабом"""
        
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(60)
        
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        # Кнопка уменьшения
        zoom_out_btn = QPushButton("➖")
        zoom_out_btn.setMaximumWidth(40)
        zoom_out_btn.clicked.connect(self.zoom_out)
        layout.addWidget(zoom_out_btn)
        
        # Слайдер масштаба
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(int(self.min_zoom * 100))
        self.zoom_slider.setMaximum(int(self.max_zoom * 100))
        self.zoom_slider.setValue(100)  # 100% = 1.0
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        layout.addWidget(self.zoom_slider)
        
        # Кнопка увеличения
        zoom_in_btn = QPushButton("➕")
        zoom_in_btn.setMaximumWidth(40)
        zoom_in_btn.clicked.connect(self.zoom_in)
        layout.addWidget(zoom_in_btn)
        
        # Кнопка сброса масштаба
        reset_zoom_btn = QPushButton("100%")
        reset_zoom_btn.setMaximumWidth(50)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        layout.addWidget(reset_zoom_btn)
        
        # Label с текущим масштабом
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.zoom_label)
        
        return panel
    
    def create_info_panel(self):
        """Создание панели информации об изображении"""
        
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(40)
        
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        # Информация о размере
        self.size_label = QLabel("Размер: —")
        layout.addWidget(self.size_label)
        
        # Информация о формате
        self.format_label = QLabel("Формат: —")
        layout.addWidget(self.format_label)
        
        # Информация о координатах курсора
        self.coords_label = QLabel("Координаты: —")
        layout.addWidget(self.coords_label)
        
        layout.addStretch()
        
        return panel
    
    def set_image(self, image):
        """Установка изображения для отображения"""
        
        try:
            if image is None:
                self.clear_image()
                return
            
            self.current_image = image.copy()
            
            # Конвертация в QPixmap
            self.current_pixmap = self.opencv_to_qpixmap(image)
            
            # Обновление отображения
            self.update_display()
            
            # Обновление информации
            self.update_image_info()
            
        except Exception as e:
            self.clear_image()
            self.size_label.setText(f"Ошибка: {str(e)}")
    
    def clear_image(self):
        """Очистка отображения"""
        
        self.current_image = None
        self.current_pixmap = None
        
        self.image_label.clear()
        self.image_label.setText("📁 Загрузите изображение\nили включите камеру")
        
        self.size_label.setText("Размер: —")
        self.format_label.setText("Формат: —")
        self.coords_label.setText("Координаты: —")
    
    def update_display(self):
        """Обновление отображения с текущим масштабом"""
        
        if self.current_pixmap is None:
            return
        
        # Применение масштаба
        scaled_pixmap = self.current_pixmap.scaled(
            self.current_pixmap.size() * self.zoom_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Установка изображения
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
    
    def update_image_info(self):
        """Обновление информации об изображении"""
        
        if self.current_image is None:
            return
        
        height, width = self.current_image.shape[:2]
        channels = len(self.current_image.shape)
        
        # Размер
        self.size_label.setText(f"Размер: {width}×{height}")
        
        # Формат
        if channels == 3:
            format_text = "Цветное (BGR)"
        elif channels == 1:
            format_text = "Оттенки серого"
        else:
            format_text = f"{channels} каналов"
        
        self.format_label.setText(f"Формат: {format_text}")
    
    def opencv_to_qpixmap(self, cv_image):
        """Конвертация OpenCV изображения в QPixmap"""
        
        if len(cv_image.shape) == 3:
            # Цветное изображение
            height, width, channels = cv_image.shape
            bytes_per_line = channels * width
            
            # OpenCV использует BGR, Qt использует RGB
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            qt_image = QImage(
                rgb_image.data, width, height, 
                bytes_per_line, QImage.Format_RGB888
            )
        else:
            # Оттенки серого
            height, width = cv_image.shape
            bytes_per_line = width
            qt_image = QImage(
                cv_image.data, width, height, 
                bytes_per_line, QImage.Format_Grayscale8
            )
        
        return QPixmap.fromImage(qt_image)
    
    def zoom_in(self):
        """Увеличение масштаба"""
        
        new_zoom = min(self.zoom_factor * 1.25, self.max_zoom)
        self.set_zoom(new_zoom)
    
    def zoom_out(self):
        """Уменьшение масштаба"""
        
        new_zoom = max(self.zoom_factor / 1.25, self.min_zoom)
        self.set_zoom(new_zoom)
    
    def reset_zoom(self):
        """Сброс масштаба к 100%"""
        
        self.set_zoom(1.0)
    
    def set_zoom(self, zoom_factor):
        """Установка конкретного масштаба"""
        
        zoom_factor = max(self.min_zoom, min(zoom_factor, self.max_zoom))
        
        if abs(zoom_factor - self.zoom_factor) < 0.01:
            return
        
        self.zoom_factor = zoom_factor
        
        # Обновление отображения
        self.update_display()
        
        # Обновление элементов управления
        self.zoom_slider.setValue(int(zoom_factor * 100))
        self.zoom_label.setText(f"{int(zoom_factor * 100)}%")
        
        # Испускание сигнала
        self.zoom_changed.emit(zoom_factor)
    
    def on_zoom_slider_changed(self, value):
        """Обработка изменения слайдера масштаба"""
        
        zoom_factor = value / 100.0
        self.set_zoom(zoom_factor)
    
    def on_image_click(self, event):
        """Обработка клика по изображению"""
        
        if self.current_image is None:
            return
        
        # Получение координат клика
        x = event.pos().x()
        y = event.pos().y()
        
        # Преобразование координат с учетом масштаба
        if self.zoom_factor != 0:
            original_x = int(x / self.zoom_factor)
            original_y = int(y / self.zoom_factor)
            
            # Проверка границ
            height, width = self.current_image.shape[:2]
            if 0 <= original_x < width and 0 <= original_y < height:
                self.coords_label.setText(f"Координаты: ({original_x}, {original_y})")
                self.image_clicked.emit(original_x, original_y)
            else:
                self.coords_label.setText("Координаты: —")
    
    def wheelEvent(self, event):
        """Обработка прокрутки колеса мыши для масштабирования"""
        
        if self.current_pixmap is None:
            return
        
        # Получение направления прокрутки
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def update_image(self, image):
        """Слот для обновления изображения (для подключения к сигналам)"""
        
        self.set_image(image)
    
    def get_current_image(self):
        """Получение текущего изображения"""
        
        return self.current_image
    
    def get_zoom_factor(self):
        """Получение текущего масштаба"""
        
        return self.zoom_factor
