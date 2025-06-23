"""
Модуль обработки ошибок и настройки логирования

Обеспечивает централизованную обработку ошибок
и настройку системы логирования.
"""

import logging
import sys
import os
import platform
import cv2
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.INFO):
    """
    Настройка системы логирования
    
    Args:
        log_level: Уровень логирования
    """
    
    # Создание директории для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Имя файла лога с текущей датой
    log_filename = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Формат логирования
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Вывод в файл
            logging.FileHandler(log_filename, encoding='utf-8'),
            # Вывод в консоль
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Отключение логов от matplotlib и других библиотек
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Система логирования инициализирована")


class ErrorHandler:
    """Класс для централизованной обработки ошибок"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
        self.error_history = []
    
    def handle_error(self, error, context="", critical=False):
        """
        Обработка ошибки
        
        Args:
            error: Объект исключения
            context: Контекст возникновения ошибки
            critical: Критическая ли ошибка
            
        Returns:
            Строка с описанием ошибки
        """
        
        self.error_count += 1
        
        # Формирование сообщения об ошибке
        error_type = type(error).__name__
        error_msg = str(error)
        
        if context:
            full_msg = f"{context}: {error_type} - {error_msg}"
        else:
            full_msg = f"{error_type}: {error_msg}"
        
        # Добавление в историю
        self.error_history.append({
            'timestamp': datetime.now(),
            'type': error_type,
            'message': error_msg,
            'context': context,
            'critical': critical
        })
        
        # Логирование
        if critical:
            self.logger.critical(full_msg, exc_info=True)
        else:
            self.logger.error(full_msg, exc_info=True)
        
        return full_msg
    
    def get_user_friendly_message(self, error):
        """
        Получение понятного пользователю сообщения об ошибке
        
        Args:
            error: Объект исключения
            
        Returns:
            Строка с сообщением для пользователя
        """
        
        error_type = type(error).__name__
        
        # Словарь сообщений для различных типов ошибок
        user_messages = {
            'FileNotFoundError': 'Файл не найден. Проверьте путь к файлу.',
            'PermissionError': 'Нет прав доступа к файлу.',
            'ValueError': 'Некорректные входные данные.',
            'MemoryError': 'Недостаточно памяти для выполнения операции.',
            'cv2.error': 'Ошибка обработки изображения.',
            'RuntimeError': 'Ошибка выполнения операции.',
            'ImportError': 'Не удалось загрузить необходимый модуль.',
            'AttributeError': 'Внутренняя ошибка программы.',
            'TypeError': 'Некорректный тип данных.',
            'OSError': 'Ошибка операционной системы.'
        }
        
        # Получение сообщения
        if error_type in user_messages:
            base_msg = user_messages[error_type]
        else:
            base_msg = 'Произошла неизвестная ошибка.'
        
        # Добавление деталей для некоторых типов ошибок
        if hasattr(error, 'filename') and error.filename:
            base_msg += f"\nФайл: {error.filename}"
        
        return base_msg
    
    def log_system_info(self):
        """Логирование информации о системе"""
        
        try:
            info = {
                'Python': platform.python_version(),
                'Platform': platform.platform(),
                'OpenCV': cv2.__version__,
                'Qt': QT_VERSION_STR,
                'PyQt': PYQT_VERSION_STR
            }
            
            self.logger.info("Информация о системе:")
            for key, value in info.items():
                self.logger.info(f"  {key}: {value}")
                
        except Exception as e:
            self.logger.warning(f"Не удалось получить информацию о системе: {e}")
    
    def get_error_statistics(self):
        """
        Получение статистики по ошибкам
        
        Returns:
            Словарь со статистикой
        """
        
        stats = {
            'total_errors': self.error_count,
            'critical_errors': sum(1 for e in self.error_history if e['critical']),
            'error_types': {}
        }
        
        # Подсчет по типам ошибок
        for error in self.error_history:
            error_type = error['type']
            if error_type in stats['error_types']:
                stats['error_types'][error_type] += 1
            else:
                stats['error_types'][error_type] = 1
        
        return stats
    
    def clear_error_history(self):
        """Очистка истории ошибок"""
        
        self.error_history.clear()
        self.error_count = 0
        self.logger.info("История ошибок очищена")
    
    def save_error_report(self, filepath=None):
        """
        Сохранение отчета об ошибках
        
        Args:
            filepath: Путь для сохранения отчета
        """
        
        if not filepath:
            filepath = f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("ОТЧЕТ ОБ ОШИБКАХ\n")
                f.write("=" * 50 + "\n")
                f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Всего ошибок: {self.error_count}\n")
                f.write("=" * 50 + "\n\n")
                
                for error in self.error_history:
                    f.write(f"Время: {error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Тип: {error['type']}\n")
                    f.write(f"Сообщение: {error['message']}\n")
                    f.write(f"Контекст: {error['context']}\n")
                    f.write(f"Критическая: {'Да' if error['critical'] else 'Нет'}\n")
                    f.write("-" * 50 + "\n")
            
            self.logger.info(f"Отчет об ошибках сохранен: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения отчета: {e}")
