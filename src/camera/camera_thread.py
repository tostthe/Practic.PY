"""
Поток для работы с веб-камерой

Альтернативная реализация захвата видео в отдельном потоке.
"""

import cv2
import logging
from PyQt5.QtCore import QThread, pyqtSignal


class CameraThread(QThread):
    """Поток для захвата видео с камеры"""
    
    # Сигналы
    frame_captured = pyqtSignal(object)  # Новый кадр
    error_occurred = pyqtSignal(str)     # Ошибка
    
    def __init__(self, camera_index=0):
        super().__init__()
        
        self.camera_index = camera_index
        self.capture = None
        self.is_running = False
        
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Основной цикл потока"""
        
        try:
            # Открытие камеры
            self.capture = cv2.VideoCapture(self.camera_index)
            
            if not self.capture.isOpened():
                raise RuntimeError("Не удалось открыть камеру")
            
            self.is_running = True
            
            while self.is_running:
                ret, frame = self.capture.read()
                
                if ret:
                    self.frame_captured.emit(frame)
                else:
                    self.error_occurred.emit("Не удалось получить кадр")
                    break
                
                # Небольшая задержка для контроля FPS
                self.msleep(33)  # ~30 FPS
                
        except Exception as e:
            error_msg = f"Ошибка в потоке камеры: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        
        finally:
            self.cleanup()
    
    def stop(self):
        """Остановка потока"""
        
        self.is_running = False
        self.wait()  # Ожидание завершения потока
    
    def cleanup(self):
        """Освобождение ресурсов"""
        
        if self.capture:
            self.capture.release()
            self.capture = None