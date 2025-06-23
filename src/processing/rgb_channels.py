"""
Модуль для работы с RGB каналами изображений

Содержит функции для выделения и обработки
отдельных цветовых каналов.
"""

import cv2
import numpy as np


class RGBProcessor:
    """Класс для работы с RGB каналами"""
    
    @staticmethod
    def extract_channel(image, channel):
        """
        Извлечение отдельного цветового канала
        
        Args:
            image: Исходное изображение
            channel: Канал ('red', 'green', 'blue')
            
        Returns:
            Изображение с выделенным каналом
        """
        
        if image is None or len(image.shape) != 3:
            return image
        
        # Создание черного изображения
        result = np.zeros_like(image)
        
        # Копирование нужного канала
        if channel == 'red':
            result[:, :, 2] = image[:, :, 2]
        elif channel == 'green':
            result[:, :, 1] = image[:, :, 1]
        elif channel == 'blue':
            result[:, :, 0] = image[:, :, 0]
        
        return result
    
    @staticmethod
    def get_channel_grayscale(image, channel):
        """
        Получение канала в оттенках серого
        
        Args:
            image: Исходное изображение
            channel: Канал ('red', 'green', 'blue')
            
        Returns:
            Канал в оттенках серого
        """
        
        if image is None or len(image.shape) != 3:
            return image
        
        if channel == 'red':
            return image[:, :, 2]
        elif channel == 'green':
            return image[:, :, 1]
        elif channel == 'blue':
            return image[:, :, 0]
        
        return image
    
    @staticmethod
    def merge_channels(red, green, blue):
        """
        Объединение каналов в RGB изображение
        
        Args:
            red: Красный канал
            green: Зеленый канал
            blue: Синий канал
            
        Returns:
            RGB изображение
        """
        
        return cv2.merge([blue, green, red])