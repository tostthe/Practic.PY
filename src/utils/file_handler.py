"""
Модуль для работы с файлами изображений

Обеспечивает загрузку и сохранение изображений,
работу с различными форматами файлов.
"""

import os
import cv2
import logging
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog


class FileHandler:
    """Класс для работы с файлами изображений"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Поддерживаемые форматы
        self.supported_formats = {
            'images': ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif'],
            'all': ['*.*']
        }
    
    def open_file_dialog(self, parent=None):
        """
        Открытие диалога выбора файла
        
        Args:
            parent: Родительское окно
            
        Returns:
            Путь к выбранному файлу или пустая строка
        """
        
        try:
            # Формирование фильтра файлов
            image_filter = "Изображения (" + " ".join(self.supported_formats['images']) + ")"
            all_filter = "Все файлы (*.*)"
            filter_string = f"{image_filter};;{all_filter}"
            
            # Открытие диалога
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                "Выберите изображение",
                "",
                filter_string
            )
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Ошибка открытия диалога: {str(e)}")
            return ""
    
    def save_file_dialog(self, parent=None):
        """
        Открытие диалога сохранения файла
        
        Args:
            parent: Родительское окно
            
        Returns:
            Путь для сохранения файла или пустая строка
        """
        
        try:
            # Формирование фильтра файлов
            filters = [
                "PNG изображение (*.png)",
                "JPEG изображение (*.jpg *.jpeg)",
                "BMP изображение (*.bmp)",
                "TIFF изображение (*.tiff *.tif)"
            ]
            filter_string = ";;".join(filters)
            
            # Открытие диалога
            file_path, selected_filter = QFileDialog.getSaveFileName(
                parent,
                "Сохранить изображение",
                "",
                filter_string
            )
            
            # Добавление расширения, если не указано
            if file_path and not Path(file_path).suffix:
                if "PNG" in selected_filter:
                    file_path += ".png"
                elif "JPEG" in selected_filter:
                    file_path += ".jpg"
                elif "BMP" in selected_filter:
                    file_path += ".bmp"
                elif "TIFF" in selected_filter:
                    file_path += ".tiff"
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Ошибка диалога сохранения: {str(e)}")
            return ""
    
    def load_image(self, file_path):
        """
        Загрузка изображения из файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Загруженное изображение (numpy array) или None
        """
        
        try:
            if not file_path or not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            
            # Загрузка изображения
            # cv2.IMREAD_UNCHANGED сохраняет альфа-канал если есть
            image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            
            if image is None:
                raise ValueError("Не удалось загрузить изображение")
            
            # Если изображение имеет альфа-канал, конвертируем в BGR
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            
            self.logger.info(f"Изображение загружено: {file_path}")
            return image
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки изображения: {str(e)}")
            return None
    
    def save_image(self, image, file_path):
        """
        Сохранение изображения в файл
        
        Args:
            image: Изображение для сохранения
            file_path: Путь для сохранения
            
        Returns:
            True в случае успеха, False в случае ошибки
        """
        
        try:
            if image is None:
                raise ValueError("Нет изображения для сохранения")
            
            if not file_path:
                raise ValueError("Не указан путь для сохранения")
            
            # Создание директории если не существует
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Определение параметров сохранения по расширению
            ext = Path(file_path).suffix.lower()
            
            if ext in ['.jpg', '.jpeg']:
                # Для JPEG устанавливаем качество
                params = [cv2.IMWRITE_JPEG_QUALITY, 95]
            elif ext == '.png':
                # Для PNG устанавливаем уровень сжатия
                params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
            else:
                params = []
            
            # Сохранение изображения
            success = cv2.imwrite(file_path, image, params)
            
            if not success:
                raise RuntimeError("cv2.imwrite вернул False")
            
            self.logger.info(f"Изображение сохранено: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения изображения: {str(e)}")
            return False
    
    def get_file_info(self, file_path):
        """
        Получение информации о файле изображения
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Словарь с информацией о файле
        """
        
        try:
            if not os.path.exists(file_path):
                return None
            
            # Получение информации о файле
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # Загрузка изображения для получения размеров
            image = cv2.imread(file_path)
            if image is None:
                return None
            
            height, width = image.shape[:2]
            channels = 1 if len(image.shape) == 2 else image.shape[2]
            
            info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'width': width,
                'height': height,
                'channels': channels,
                'format': Path(file_path).suffix.upper()[1:]
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о файле: {str(e)}")
            return None
    
    def validate_image_file(self, file_path):
        """
        Проверка валидности файла изображения
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если файл валиден, False в противном случае
        """
        
        try:
            if not os.path.exists(file_path):
                return False
            
            # Проверка расширения
            ext = Path(file_path).suffix.lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
            
            if ext not in valid_extensions:
                return False
            
            # Попытка загрузить изображение
            image = cv2.imread(file_path)
            
            return image is not None
            
        except Exception:
            return False