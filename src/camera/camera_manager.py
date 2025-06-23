"""
Менеджер работы с веб-камерой

Управляет захватом видео с камеры, предоставляет
интерфейс для получения кадров.
"""

import cv2
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class CameraManager(QObject):
    """Класс для управления веб-камерой"""
    
    # Сигналы
    frame_ready = pyqtSignal(object)  # Новый кадр готов
    error_occurred = pyqtSignal(str)  # Произошла ошибка
    camera_started = pyqtSignal()    # Камера запущена
    camera_stopped = pyqtSignal()    # Камера остановлена
    
    def __init__(self, camera_index=0):
        super().__init__()
        
        self.camera_index = camera_index
        self.capture = None
        self.timer = None
        self.is_capturing = False
        
        self.logger = logging.getLogger(__name__)
        
        # Параметры захвата
        self.fps = 30  # Кадров в секунду
        self.frame_interval = int(1000 / self.fps)  # Интервал в миллисекундах
    
    def start_capture(self):
        """Запуск захвата видео с камеры"""
        
        try:
            if self.is_capturing:
                self.logger.warning("Камера уже запущена")
                return
            
            # Открытие камеры
            self.capture = cv2.VideoCapture(self.camera_index)
            
            if not self.capture.isOpened():
                raise RuntimeError("Не удалось открыть камеру")
            
            # Настройка параметров камеры
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Создание и запуск таймера
            self.timer = QTimer()
            self.timer.timeout.connect(self._capture_frame)
            self.timer.start(self.frame_interval)
            
            self.is_capturing = True
            self.logger.info("Захват с камеры запущен")
            self.camera_started.emit()  # Испускание сигнала о запуске
            
        except Exception as e:
            error_msg = f"Ошибка запуска камеры: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self._cleanup()
    
    def stop_capture(self):
        """Остановка захвата видео"""
        
        try:
            if not self.is_capturing:
                return
            
            # Остановка таймера
            if self.timer:
                self.timer.stop()
                self.timer = None
            
            # Закрытие камеры
            if self.capture:
                self.capture.release()
                self.capture = None
            
            self.is_capturing = False
            self.logger.info("Захват с камеры остановлен")
            self.camera_stopped.emit()  # Испускание сигнала об остановке
            
        except Exception as e:
            error_msg = f"Ошибка остановки камеры: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def capture_single_frame(self):
        """
        Захват одного кадра с камеры
        
        Returns:
            Захваченный кадр или None в случае ошибки
        """
        
        try:
            # Явная проверка состояния камеры
            if not self.is_capturing or not self.capture:
                raise RuntimeError("Камера не активна")
            
            if not self.capture.isOpened():
                raise RuntimeError("Камера недоступна")
            
            ret, frame = self.capture.read()
            
            if ret:
                return frame.copy()
            else:
                raise RuntimeError("Не удалось захватить кадр")
                
        except Exception as e:
            error_msg = f"Ошибка захвата кадра: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None
    
    def _capture_frame(self):
        """Внутренний метод для захвата и отправки кадра"""
        
        try:
            if not self.capture or not self.capture.isOpened():
                raise RuntimeError("Камера не доступна")
            
            ret, frame = self.capture.read()
            
            if ret:
                # Отправка кадра через сигнал
                self.frame_ready.emit(frame)
            else:
                raise RuntimeError("Не удалось прочитать кадр")
                
        except Exception as e:
            error_msg = f"Ошибка чтения кадра: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.stop_capture()
    
    def _cleanup(self):
        """Очистка ресурсов"""
        
        try:
            if self.timer:
                self.timer.stop()
                self.timer = None
            
            if self.capture:
                self.capture.release()
                self.capture = None
            
            self.is_capturing = False
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {str(e)}")
    
    def get_available_cameras(self):
        """
        Получение списка доступных камер
        
        Returns:
            Список индексов доступных камер
        """
        
        available_cameras = []
        
        # Проверяем первые 10 индексов
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        
        return available_cameras
    
    def set_camera_index(self, index):
        """
        Установка индекса камеры
        
        Args:
            index: Индекс камеры
        """
        
        if self.is_capturing:
            self.stop_capture()
        
        self.camera_index = index
        self.logger.info(f"Установлен индекс камеры: {index}")
    
    def __del__(self):
        """Деструктор для освобождения ресурсов"""
        
        self._cleanup()