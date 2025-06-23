"""
Модуль валидации данных

Содержит классы и функции для проверки корректности
входных данных и изображений.
"""

import cv2
import numpy as np


class ImageValidator:
    """Класс для валидации изображений"""
    
    @staticmethod
    def is_valid_image(image):
        """
        Проверка валидности изображения
        
        Args:
            image: Изображение для проверки
            
        Returns:
            True если изображение валидно, False в противном случае
        """
        
        if image is None:
            return False
        
        if not isinstance(image, np.ndarray):
            return False
        
        if len(image.shape) not in [2, 3]:
            return False
        
        if image.size == 0:
            return False
        
        return True
    
    @staticmethod
    def validate_image_size(image, max_width=8000, max_height=8000):
        """
        Проверка размера изображения
        
        Args:
            image: Изображение для проверки
            max_width: Максимальная ширина
            max_height: Максимальная высота
            
        Returns:
            Tuple (is_valid, error_message)
        """
        
        if not ImageValidator.is_valid_image(image):
            return False, "Невалидное изображение"
        
        height, width = image.shape[:2]
        
        if width > max_width:
            return False, f"Ширина изображения ({width}) превышает максимальную ({max_width})"
        
        if height > max_height:
            return False, f"Высота изображения ({height}) превышает максимальную ({max_height})"
        
        return True, ""
    
    @staticmethod
    def validate_coordinates(x, y, image):
        """
        Проверка координат в пределах изображения
        
        Args:
            x: X координата
            y: Y координата
            image: Изображение
            
        Returns:
            True если координаты валидны
        """
        
        if not ImageValidator.is_valid_image(image):
            return False
        
        height, width = image.shape[:2]
        
        return 0 <= x < width and 0 <= y < height
    
    @staticmethod
    def validate_resize_params(new_width, new_height):
        """
        Валидация параметров изменения размера
        
        Args:
            new_width: Новая ширина
            new_height: Новая высота
            
        Returns:
            Tuple (is_valid, error_message)
        """
        
        if not isinstance(new_width, (int, float)) or not isinstance(new_height, (int, float)):
            return False, "Размеры должны быть числами"
        
        if new_width <= 0 or new_height <= 0:
            return False, "Размеры должны быть положительными"
        
        if new_width > 8000 or new_height > 8000:
            return False, "Размеры слишком большие (максимум 8000)"
        
        return True, ""