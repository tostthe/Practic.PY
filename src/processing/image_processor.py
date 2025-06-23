"""
Основной модуль обработки изображений

Содержит класс ImageProcessor с методами для обработки изображений,
включая работу с RGB каналами и функции варианта.
"""

import cv2
import numpy as np
import logging
from utils.validators import ImageValidator


class ImageProcessor:
    """Класс для обработки изображений"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
        
        # Получаем текущее изображение (оригинал или обработанное)
        current_img = self.parent().processed_image if self.parent().processed_image is not None else self.current_image
        
        if current_img is None:
            return
        
        # Создаем временное изображение для отображения
        display_image = self.create_channel_display(current_img, channel)
        self.parent().image_viewer.set_image(display_image)

    def create_channel_display(self, image, channel):
        """Создает изображение для отображения выбранного канала без модификации оригинала"""
        if channel == 'original':
            return image.copy()
        
        if len(image.shape) != 3:
            return image.copy()
        
        # Создаем копию для отображения
        display = image.copy()
        
        if channel == 'red':
            display[:, :, 0] = 0  # Синий
            display[:, :, 1] = 0  # Зеленый
        elif channel == 'green':
            display[:, :, 0] = 0  # Синий
            display[:, :, 2] = 0  # Красный
        elif channel == 'blue':
            display[:, :, 1] = 0  # Зеленый
            display[:, :, 2] = 0  # Красный
        
        return display
        
    def get_channel_image(self, image, channel):
        """
        Получение изображения с выделенным RGB каналом
        
        Args:
            image: Исходное изображение
            channel: Название канала ('original', 'red', 'green', 'blue')
            
        Returns:
            Обработанное изображение
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            if channel == 'original':
                return image.copy()
            
            # Проверка, что изображение цветное
            if len(image.shape) != 3:
                self.logger.warning("Изображение не цветное, возвращаем оригинал")
                return image.copy()
            
            # Создание черного изображения того же размера
            result = np.zeros_like(image)
            
            # Выделение нужного канала
            if channel == 'red':
                result[:, :, 2] = image[:, :, 2]  # В OpenCV порядок BGR
            elif channel == 'green':
                result[:, :, 1] = image[:, :, 1]
            elif channel == 'blue':
                result[:, :, 0] = image[:, :, 0]
            else:
                self.logger.warning(f"Неизвестный канал: {channel}")
                return image.copy()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при выделении канала: {str(e)}")
            raise
    
    def resize_image(self, image, new_width, new_height):
        """
        Изменение размера изображения
        
        Args:
            image: Исходное изображение
            new_width: Новая ширина
            new_height: Новая высота
            
        Returns:
            Изображение с измененным размером
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Валидация параметров
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Размеры должны быть положительными")
            
            if new_width > 8000 or new_height > 8000:
                raise ValueError("Размеры слишком большие (максимум 8000)")
            
            # Изменение размера
            resized = cv2.resize(image, (new_width, new_height), 
                               interpolation=cv2.INTER_LINEAR)
            
            self.logger.info(f"Размер изменен на {new_width}x{new_height}")
            return resized
            
        except Exception as e:
            self.logger.error(f"Ошибка при изменении размера: {str(e)}")
            raise
    
    def decrease_brightness(self, image, value):
        """
        Понижение яркости изображения
        
        Args:
            image: Исходное изображение
            value: Значение понижения яркости (0-100)
            
        Returns:
            Изображение с пониженной яркостью
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Валидация параметра
            value = max(0, min(100, value))
            
            # Создание копии изображения
            result = image.copy().astype(np.float32)
            
            # Понижение яркости
            # Применяем коэффициент к каждому пикселю
            factor = 1.0 - (value / 100.0)
            result = result * factor
            
            # Ограничение значений в диапазоне [0, 255]
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            self.logger.info(f"Яркость понижена на {value}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при понижении яркости: {str(e)}")
            raise
    
    def draw_blue_rectangle(self, image, top_left_x, top_left_y, width, height):
        """
        Рисование синего прямоугольника на изображении
        
        Args:
            image: Исходное изображение
            top_left_x: X координата верхнего левого угла
            top_left_y: Y координата верхнего левого угла
            width: Ширина прямоугольника
            height: Высота прямоугольника
            
        Returns:
            Изображение с нарисованным прямоугольником
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Создание копии изображения
            result = image.copy()
            
            # Валидация параметров
            img_height, img_width = image.shape[:2]
            
            if top_left_x < 0 or top_left_x >= img_width:
                raise ValueError(f"X координата вне границ изображения (0-{img_width-1})")
            
            if top_left_y < 0 or top_left_y >= img_height:
                raise ValueError(f"Y координата вне границ изображения (0-{img_height-1})")
            
            if width <= 0 or height <= 0:
                raise ValueError("Ширина и высота должны быть положительными")
            
            # Расчет нижнего правого угла
            bottom_right_x = top_left_x + width
            bottom_right_y = top_left_y + height
            
            if bottom_right_x >= img_width:
                raise ValueError(f"Прямоугольник выходит за границы по ширине")
            
            if bottom_right_y >= img_height:
                raise ValueError(f"Прямоугольник выходит за границы по высоте")
            
            # Рисование прямоугольника
            # Синий цвет в BGR формате: (255, 0, 0)
            color = (150, 60, 0)
            thickness = 3  # Толщина линии
            
            cv2.rectangle(
                result, 
                (top_left_x, top_left_y), 
                (bottom_right_x, bottom_right_y), 
                color, 
                thickness
            )
            
            self.logger.info(f"Нарисован прямоугольник: верхний левый угол=({top_left_x}, {top_left_y}), размер={width}x{height}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при рисовании прямоугольника: {str(e)}")
            raise
    
    def rotate_image(self, image, angle):
        """
        Поворот изображения
        
        Args:
            image: Исходное изображение
            angle: Угол поворота в градусах
            
        Returns:
            Повернутое изображение
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            
            # Матрица поворота
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Поворот изображения
            rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
            
            self.logger.info(f"Изображение повернуто на {angle}°")
            return rotated
            
        except Exception as e:
            self.logger.error(f"Ошибка при повороте изображения: {str(e)}")
            raise
    
    def apply_blur(self, image, kernel_size=5):
        """
        Размытие изображения
        
        Args:
            image: Исходное изображение
            kernel_size: Размер ядра размытия
            
        Returns:
            Размытое изображение
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Проверка, что kernel_size нечетное
            if kernel_size % 2 == 0:
                kernel_size += 1
                self.logger.info(f"Размер ядра увеличен до нечетного: {kernel_size}")
                
            # Размытие
            blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
            
            self.logger.info(f"Применено размытие с ядром {kernel_size}x{kernel_size}")
            return blurred
            
        except Exception as e:
            self.logger.error(f"Ошибка при размытии изображения: {str(e)}")
            raise
    
    def crop_image(self, image, x, y, width, height):
        """
        Обрезка изображения
        
        Args:
            image: Исходное изображение
            x: X координата верхнего левого угла
            y: Y координата верхнего левого угла
            width: Ширина области обрезки
            height: Высота области обрезки
            
        Returns:
            Обрезанное изображение
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Проверка границ
            img_height, img_width = image.shape[:2]
            
            if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
                raise ValueError("Область обрезки выходит за пределы изображения")
            
            if width <= 0 or height <= 0:
                raise ValueError("Ширина и высота должны быть положительными")
            
            # Обрезка изображения
            cropped = image[y:y+height, x:x+width]
            
            self.logger.info(f"Изображение обрезано: x={x}, y={y}, width={width}, height={height}")
            return cropped
            
        except Exception as e:
            self.logger.error(f"Ошибка при обрезке изображения: {str(e)}")
            raise
    
    def add_black_border(self, image, top, bottom, left, right):
        """
        Добавление черной рамки к изображению
        
        Args:
            image: Исходное изображение
            top: Размер верхней границы (в пикселях)
            bottom: Размер нижней границы (в пикселях)
            left: Размер левой границы (в пикселях)
            right: Размер правой границы (в пикселях)
            
        Returns:
            Изображение с черной рамкой
        """
        try:
            if image is None or not ImageValidator.is_valid_image(image):
                raise ValueError("Невалидное изображение")
            
            # Валидация параметров
            if top < 0 or bottom < 0 or left < 0 or right < 0:
                raise ValueError("Размеры границ должны быть неотрицательными")
            
            # Определение цветов границы в зависимости от типа изображения
            if len(image.shape) == 3:  # Цветное изображение
                border_color = [0, 0, 0]  # Черный цвет в BGR
            else:  # Оттенки серого
                border_color = 0  # Черный цвет
            
            # Добавление границ
            result = cv2.copyMakeBorder(
                image,
                top, bottom, left, right,
                cv2.BORDER_CONSTANT,
                value=border_color
            )
            
            self.logger.info(f"Добавлена черная рамка: top={top}, bottom={bottom}, left={left}, right={right}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении рамки: {str(e)}")
            raise