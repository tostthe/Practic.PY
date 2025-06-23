"""
Модуль с функциями обработки изображений для вариантов

Содержит реализацию различных функций обработки
изображений согласно вариантам задания.
"""

import cv2
import numpy as np


class VariantProcessor:
    """Класс с функциями обработки для вариантов"""
    
    @staticmethod
    def resize_image(image, new_width, new_height):
        """
        Функция 1: Изменение размера изображения
        
        Args:
            image: Исходное изображение
            new_width: Новая ширина
            new_height: Новая высота
            
        Returns:
            Изображение с измененным размером
        """
        
        return cv2.resize(image, (new_width, new_height), 
                         interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def decrease_brightness(image, value):
        """
        Функция 8: Понижение яркости
        
        Args:
            image: Исходное изображение
            value: Значение понижения (0-100)
            
        Returns:
            Изображение с пониженной яркостью
        """
        
        # Преобразование в float для точных вычислений
        result = image.astype(np.float32)
        
        # Применение коэффициента яркости
        factor = 1.0 - (value / 100.0)
        result = result * factor
        
        # Ограничение значений и преобразование обратно
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def draw_blue_rectangle(image, top_left_x, top_left_y, width, height):
        """
        Функция: Рисование синего прямоугольника
        
        Args:
            image: Исходное изображение
            top_left_x: X координата верхнего левого угла
            top_left_y: Y координата верхнего левого угла
            width: Ширина прямоугольника
            height: Высота прямоугольника
            
        Returns:
            Изображение с нарисованным прямоугольником
        """
        
        result = image.copy()
        
        # Синий цвет в BGR
        color = (120, 50, 0)
        thickness = 3
        
        # Расчет нижнего правого угла
        bottom_right_x = top_left_x + width
        bottom_right_y = top_left_y + height
        
        cv2.rectangle(
            result, 
            (top_left_x, top_left_y), 
            (bottom_right_x, bottom_right_y), 
            color, 
            thickness
        )
        
        return result
    
    @staticmethod
    def rotate_image(image, angle):
        """
        Дополнительная функция: Поворот изображения
        
        Args:
            image: Исходное изображение
            angle: Угол поворота в градусах
            
        Returns:
            Повернутое изображение
        """
        
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Матрица поворота
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Поворот изображения
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        
        return rotated
    
    @staticmethod
    def apply_blur(image, kernel_size=5):
        """
        Дополнительная функция: Размытие изображения
        
        Args:
            image: Исходное изображение
            kernel_size: Размер ядра размытия
            
        Returns:
            Размытое изображение
        """
        
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)