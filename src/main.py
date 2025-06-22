import sys
import os
import logging
from pathlib import Path

# Добавление корневой папки в Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from gui.main_window import ImageProcessorWindow
from utils.error_handler import setup_logging

def main():
    """Главная функция запуска приложения"""
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Проверка зависимостей
        check_dependencies()
        
        # Создание приложения Qt
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setApplicationName("Обработка изображений")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Университет")
        
        # Создание и отображение главного окна
        window = ImageProcessorWindow()
        window.show()
        
        logger.info("Приложение успешно запущено")
        
        # Запуск основного цикла приложения
        sys.exit(app.exec_())
        
    except ImportError as e:
        error_msg = f"Ошибка импорта модулей: {e}\nПроверьте установку зависимостей"
        if 'app' in locals():
            QMessageBox.critical(None, "Ошибка запуска", error_msg)
        else:
            print(f"❌ {error_msg}")
        logger.error(error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Критическая ошибка: {e}"
        if 'app' in locals():
            QMessageBox.critical(None, "Критическая ошибка", error_msg)
        else:
            print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        sys.exit(1)

def check_dependencies():
    """Проверка установки необходимых зависимостей"""
    required_modules = {
        'cv2': 'OpenCV',
        'PyQt5': 'PyQt5',
        'numpy': 'NumPy',
        'PIL': 'Pillow'
    }
    
    missing_modules = []
    
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {name}: установлен")
        except ImportError:
            missing_modules.append(name)
            print(f"❌ {name}: не установлен")
    
    # Проверка PyTorch (опциональная)
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError:
        print("⚠️ PyTorch: не установлен (опционально)")
    
    if missing_modules:
        raise ImportError(f"Отсутствуют модули: {', '.join(missing_modules)}")
    
    print("🎉 Все зависимости установлены!")

if __name__ == "__main__":
    main()