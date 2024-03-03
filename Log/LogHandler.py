import logging
import threading

# Singleton Log Class
class LogHandler(object):
    _log_instance = None
    # Lock to ensure thread safety
    _lock = threading.Lock()  

    @classmethod
    def _get_instance(cls):
        if cls._log_instance is None:
            with cls._lock:
                # Double check locking for efficiency
                if cls._log_instance is None:  
                    cls._log_instance = cls._create_logger()
        return cls._log_instance
    
    @staticmethod
    def log_info(e):
        LogHandler._get_instance().info(e)
    
    @staticmethod
    def log_error(e):
        LogHandler._get_instance().error(e)

    @staticmethod
    def log_warning(e):
        LogHandler._get_instance().warning(e)

    @staticmethod
    def _create_logger():
        logger = logging.getLogger(__name__)
        # Set logger level to lowest level
        logger.setLevel(logging.DEBUG)  
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

       # Create a logger with INFO level hence it will log ERROR as well, a higher severity level 
        handler = logging.FileHandler("Log.log")
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)

        # Add both handlers to the logger
        logger.addHandler(handler)

        return logger