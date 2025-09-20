"""
Centralized logging configuration for WorldWeaver application.

This module provides logging setup that follows the requirements:
- Local environment: logs to both stdout and files in LOGGING_DIR
- Production environment: logs only to stdout
"""
import os
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(logger_name: str = "worldweaver", level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration based on environment.
    
    Args:
        logger_name: Name for the logger
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt= "%(asctime)s [%(levelname)s] <%(filename)s:%(lineno)s - %(funcName)s()> %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Determine environment - check multiple indicators
    is_containerized = _is_containerized_environment()
    force_console_only = is_containerized or os.getenv('DEPLOYED', '0') == '1' or os.getenv('FORCE_CONSOLE_LOGGING', '0') == '1'
    
    # Always add console handler (critical for Docker environments)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # Add file handler only if not in containerized/production environment
    if not force_console_only:
        log_dir = _get_log_directory()
        if log_dir:
            log_file = log_dir / f"{logger_name}.log"
            try:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(log_level)
                logger.addHandler(file_handler)
            except (OSError, PermissionError) as e:
                # Use console handler to log the warning since file handler failed
                console_handler.handle(logging.LogRecord(
                    name=logger_name,
                    level=logging.WARNING,
                    pathname=__file__,
                    lineno=0,
                    msg=f"Could not create file handler for {log_file}: {e}",
                    args=(),
                    exc_info=None
                ))
    
    # Ensure logger propagates to root logger
    logger.propagate = True
    
    # Configure root logger if this is the first logger being set up
    if logger_name == "worldweaver":
        _configure_root_logger(formatter, log_level)
    
    return logger


def _is_containerized_environment() -> bool:
    """
    Detect if running in a containerized environment (Docker, Kubernetes, etc.)
    
    Returns:
        True if running in a container, False otherwise
    """
    # Check for common container indicators
    container_indicators = [
        # Docker-specific
        os.path.exists('/.dockerenv'),
        # Kubernetes/container runtime indicators
        os.path.exists('/proc/1/cgroup') and any(
            'docker' in line or 'containerd' in line or 'kubepods' in line
            for line in open('/proc/1/cgroup', 'r').readlines() 
            if os.path.exists('/proc/1/cgroup')
        ),
        # Environment variables commonly set in containers
        'CONTAINER' in os.environ,
        'DOCKER_CONTAINER' in os.environ,
        # Common in Railway, Heroku, and other PaaS
        'RAILWAY_ENVIRONMENT' in os.environ,
        'DYNO' in os.environ,
        # Check if running as PID 1 (common in containers)
        os.getpid() == 1
    ]
    
    try:
        # Additional check for Docker cgroup
        if os.path.exists('/proc/self/cgroup'):
            with open('/proc/self/cgroup', 'r') as f:
                content = f.read()
                if 'docker' in content or 'containerd' in content:
                    container_indicators.append(True)
    except (OSError, IOError):
        pass
    
    return any(container_indicators)


def _configure_root_logger(formatter: logging.Formatter, level: int) -> None:
    """
    Configure the root logger to ensure all log messages are captured.
    
    Args:
        formatter: Logging formatter to use
        level: Logging level to set
    """
    root_logger = logging.getLogger()
    
    # Only configure if not already configured
    if not root_logger.handlers:
        root_logger.setLevel(level)
        
        # Add console handler to root logger as well
        root_console_handler = logging.StreamHandler(sys.stdout)
        root_console_handler.setFormatter(formatter)
        root_console_handler.setLevel(level)
        root_logger.addHandler(root_console_handler)


def _get_log_directory() -> Optional[Path]:
    """
    Get the logging directory based on LOGGING_DIR environment variable.
    Falls back to backend/logs if LOGGING_DIR is not set.
    
    Returns:
        Path to log directory or None if creation fails
    """
    # Check for LOGGING_DIR environment variable first
    logging_dir = os.getenv('LOGGING_DIR')
    
    if logging_dir:
        log_dir = Path(logging_dir)
    else:
        # Fall back to backend/logs
        project_root = Path(__file__).resolve().parents[2]
        log_dir = project_root / "backend" / "logs"
    
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        # Test write permissions
        test_file = log_dir / "test_write.tmp"
        test_file.touch()
        test_file.unlink()
        return log_dir
    except (OSError, PermissionError):
        # If we can't write to the specified directory, try a temp fallback
        try:
            import tempfile
            fallback_dir = Path(tempfile.gettempdir()) / "worldweaver_logs"
            fallback_dir.mkdir(exist_ok=True)
            return fallback_dir
        except (OSError, PermissionError):
            return None


def get_logger(name: str = "worldweaver") -> logging.Logger:
    """
    Get a logger instance with the standard configuration.
    
    Args:
        name: Logger name (will be prefixed with 'worldweaver.')
        
    Returns:
        Configured logger instance
    """
    full_name = f"worldweaver.{name}" if name != "worldweaver" else name
    return setup_logging(full_name)


# Convenience function for getting module-specific loggers
def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'routes', 'agent', 'conversation')
        
    Returns:
        Configured logger instance
    """
    return get_logger(module_name)