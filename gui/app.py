import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger.setup import setup_logging, show_log_window, get_logger

def main():
    # 初始化日志系统
    setup_logging()
    logger = get_logger()
    
    try:
        # 创建应用实例
        app = QApplication(sys.argv)
        logger.info("应用程序启动")
        
        # 创建并显示主窗口
        main_window = MainWindow()
        main_window.show()
        logger.info("主窗口已显示")
        
        # 显示日志窗口
        show_log_window()
        logger.info("日志窗口已显示")
        
        # 运行应用
        return_code = app.exec()
        logger.info(f"应用程序退出，返回码：{return_code}")
        return return_code
        
    except Exception as e:
        logger.critical("应用程序启动失败", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())