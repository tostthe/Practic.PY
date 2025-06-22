"""
Модуль настроек приложения

Содержит класс для управления настройками приложения
и их сохранения/загрузки.
"""

import json
import os
from pathlib import Path


class AppSettings:
    """Класс для управления настройками приложения"""
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            # Настройки окна
            'window': {
                'width': 1400,
                'height': 900,
                'x': 100,
                'y': 100
            },
            # Настройки камеры
            'camera': {
                'default_index': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            # Настройки обработки
            'processing': {
                'default_brightness_value': 20,
                'default_circle_radius': 50,
                'circle_color': [0, 0, 255],  # BGR
                'circle_thickness': 3
            },
            # Настройки интерфейса
            'ui': {
                'theme': 'default',
                'language': 'ru',
                'show_tooltips': True,
                'auto_save': False
            },
            # Настройки файлов
            'files': {
                'last_directory': '',
                'default_save_format': 'png',
                'jpeg_quality': 95,
                'png_compression': 9
            }
        }
        
        self.settings = self.load_settings()
    
    def load_settings(self):
        """
        Загрузка настроек из файла
        
        Returns:
            Словарь с настройками
        """
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Объединение с настройками по умолчанию
                # (на случай если добавились новые настройки)
                settings = self.default_settings.copy()
                self._deep_update(settings, loaded_settings)
                
                return settings
            else:
                return self.default_settings.copy()
                
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get(self, key, default=None):
        """
        Получение значения настройки
        
        Args:
            key: Ключ настройки (может быть вложенным, например 'window.width')
            default: Значение по умолчанию
            
        Returns:
            Значение настройки
        """
        
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """
        Установка значения настройки
        
        Args:
            key: Ключ настройки (может быть вложенным)
            value: Новое значение
        """
        
        keys = key.split('.')
        settings = self.settings
        
        # Навигация до нужного уровня
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        
        # Установка значения
        settings[keys[-1]] = value
        
        # Автосохранение
        if self.get('ui.auto_save', False):
            self.save_settings()
    
    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        
        self.settings = self.default_settings.copy()
        self.save_settings()
    
    def _deep_update(self, base_dict, update_dict):
        """
        Рекурсивное обновление словаря
        
        Args:
            base_dict: Базовый словарь
            update_dict: Словарь с обновлениями
        """
        
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def export_settings(self, filepath):
        """
        Экспорт настроек в файл
        
        Args:
            filepath: Путь для экспорта
        """
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Ошибка экспорта настроек: {e}")
    
    def import_settings(self, filepath):
        """
        Импорт настроек из файла
        
        Args:
            filepath: Путь к файлу с настройками
        """
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Проверка валидности
            if not isinstance(imported_settings, dict):
                raise ValueError("Некорректный формат файла настроек")
            
            # Обновление настроек
            self.settings = self.default_settings.copy()
            self._deep_update(self.settings, imported_settings)
            self.save_settings()
            
        except Exception as e:
            raise Exception(f"Ошибка импорта настроек: {e}")