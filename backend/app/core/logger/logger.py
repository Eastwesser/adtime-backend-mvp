import logging
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Create and configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Module-level logger instance
logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)

def error(message: str, exc_info=None, context: dict = None) -> None:
    """Log error with context."""
    extra = context or {}
    logger.error(message, exc_info=exc_info, extra={"context": extra})

def critical(message: str, exc_info: Optional[BaseException] = None, 
            context: Optional[dict] = None, stack_info: bool = False) -> None:
    """Log critical error with full context."""
    extra = context or {}
    if exc_info:
        extra['exception_type'] = exc_info.__class__.__name__
    logger.critical(
        message,
        exc_info=exc_info,
        extra={"context": extra},
        stack_info=stack_info
    )

def setup_logger(name: str) -> logging.Logger:
    """Alias for get_logger for backward compatibility"""
    return get_logger(name)

class JSONFormatter(logging.Formatter):
    """Format log records as JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, 'context') and record.context:
            log_data["context"] = record.context
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


def setup_logging(level: str = "INFO", enable_file_logging: bool = False):
    """Configure application logging"""
    
    # Clear existing handlers
    logging.root.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    logging.root.addHandler(console_handler)
    logging.root.setLevel(getattr(logging, level.upper()))
    
    # File logging for production
    if enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler(
            "logs/app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(JSONFormatter())
        logging.root.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

# Initialize logging
setup_logging(level="INFO", enable_file_logging=False)