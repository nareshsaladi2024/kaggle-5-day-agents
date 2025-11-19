"""
Logging configuration utility for ADK agents.

This module provides a reusable function to configure logging for ADK agents.
- Local development: Logs to file (file_only=True)
- Cloud deployments (Vertex AI/Cloud Run): Logs to stdout/stderr for Cloud Logging (file_only=False)

Log level can be configured via environment variable or function parameter.
"""

import logging
import os
from typing import Optional, Union


def _is_cloud_environment() -> bool:
    """
    Detect if running in a Google Cloud environment (Vertex AI or Cloud Run).
    
    Returns:
        True if running in cloud, False otherwise
    """
    # Check for common cloud environment indicators
    cloud_indicators = [
        'GOOGLE_CLOUD_PROJECT',
        'GCP_PROJECT',
        'CLOUD_RUN_SERVICE',
        'K_SERVICE',  # Cloud Run service name
        'VERTEX_AI_ENDPOINT',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    # If any cloud indicator is set, assume cloud environment
    # But also check if explicitly set via environment variable
    explicit_cloud = os.environ.get('ADK_CLOUD_MODE', '').upper()
    if explicit_cloud in ('TRUE', '1', 'YES'):
        return True
    if explicit_cloud in ('FALSE', '0', 'NO'):
        return False
    
    # Auto-detect based on environment variables
    return any(os.environ.get(indicator) for indicator in cloud_indicators)


def _get_log_level(level: Union[str, int, None] = None) -> int:
    """
    Convert log level string to logging constant.
    
    Args:
        level: Log level as string ("DEBUG", "INFO", "WARNING", "ERROR") or int
    
    Returns:
        Logging level constant
    """
    if level is None:
        # Check environment variable first
        env_level = os.environ.get('ADK_LOG_LEVEL', 'DEBUG').upper()
        level = env_level
    
    if isinstance(level, str):
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level.upper(), logging.DEBUG)
    
    return level if isinstance(level, int) else logging.DEBUG


def setup_adk_logging(
    agent_name: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: Union[str, int, None] = None,
    file_only: Optional[bool] = None,
    cloud_mode: Optional[bool] = None
) -> None:
    """
    Configure logging for ADK agents.
    
    This function sets up logging to capture:
    - Events and traces (DEBUG level)
    - Request/Response details (DEBUG level)
    - Token usage information (DEBUG level)
    - Metadata and model interactions (DEBUG level)
    - HTTP request/response details (DEBUG level)
    
    **Local vs Cloud Deployment:**
    - Local: Logs to file (file_only=True) - default behavior
    - Cloud (Vertex AI/Cloud Run): Logs to stdout/stderr (file_only=False) for Cloud Logging
    
    The function auto-detects cloud environment, or you can explicitly set it.
    
    Log level can be set via:
    1. Function parameter: log_level="DEBUG" or log_level=logging.DEBUG
    2. Environment variable: ADK_LOG_LEVEL=DEBUG (or INFO, WARNING, ERROR)
    3. Default: DEBUG if not specified
    
    Args:
        agent_name: Optional name of the agent (for logging identification)
        log_file: Optional path to log file. If None, uses ADK's default location (local only).
        log_level: Logging level as string ("DEBUG", "INFO") or int (logging.DEBUG, etc.)
                  If None, reads from ADK_LOG_LEVEL environment variable or defaults to DEBUG
        file_only: If True, logs only to file (local). If False, logs to stdout/stderr (cloud).
                  If None, auto-detects based on environment (default: None)
        cloud_mode: Explicitly set cloud mode. If None, auto-detects. Overrides file_only.
    
    Examples:
        >>> from utility.logging_config import setup_adk_logging
        >>> # Auto-detect (local or cloud)
        >>> setup_adk_logging(agent_name="MyAgent")
        >>> 
        >>> # Explicitly set for cloud deployment
        >>> setup_adk_logging(agent_name="MyAgent", cloud_mode=True)
        >>> 
        >>> # Explicitly set for local development
        >>> setup_adk_logging(agent_name="MyAgent", file_only=True)
        >>> 
        >>> # Set log level
        >>> setup_adk_logging(agent_name="MyAgent", log_level="INFO")
    """
    # Convert log level to int
    actual_log_level = _get_log_level(log_level)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(actual_log_level)
    
    # Determine log file location (only for local/file logging)
    if file_only and log_file is None:
        # ADK creates log files in: %TEMP%\agents_log\agent.latest.log
        log_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'agents_log')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'agent.latest.log')
    elif not file_only:
        # In cloud mode, we don't need a log file
        log_file = None
    
    # Configure handlers based on mode
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if file_only:
        # Local mode: Remove StreamHandlers, use file handler
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)
            elif isinstance(handler, logging.FileHandler):
                # Remove any existing file handlers for the same file to avoid duplicates
                handler_path = getattr(handler, 'baseFilename', None) or getattr(
                    getattr(handler, 'stream', None), 'name', None
                )
                if handler_path and log_file and log_file in str(handler_path):
                    root_logger.removeHandler(handler)
        
        # Create and add file handler
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(actual_log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    else:
        # Cloud mode: Use StreamHandler (stdout/stderr) for Cloud Logging
        # Remove file handlers
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
        
        # Add StreamHandler if not already present
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) for h in root_logger.handlers
        )
        if not has_stream_handler:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(actual_log_level)
            stream_handler.setFormatter(formatter)
            root_logger.addHandler(stream_handler)
        else:
            # Update existing stream handler
            for handler in root_logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(actual_log_level)
                    handler.setFormatter(formatter)
    
    # Set DEBUG level for ADK and related modules explicitly
    loggers_to_debug = [
        'adk', 'google.adk', 'google_adk',
        'google.genai', 'google.genai.types', 'google.genai._client',
        'google.genai.models', 'google.genai.google_llm',
        'httpx', 'httpcore', 'urllib3'
    ]
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(actual_log_level)
        
        if file_only:
            # Remove StreamHandlers from child loggers (only keep file handlers)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler):
                    logger.removeHandler(handler)
                elif isinstance(handler, logging.FileHandler):
                    handler.setLevel(actual_log_level)
        
        # Propagate to root logger so file handler catches it
        logger.propagate = True
    
    # Ensure all root logger handlers are set correctly
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(actual_log_level)
        elif file_only and not isinstance(handler, logging.FileHandler):
            # Remove any non-file handlers if file_only is True
            root_logger.removeHandler(handler)
    
    # Log that logging is enabled
    level_name = logging.getLevelName(actual_log_level)
    mode = "cloud (stdout/stderr)" if not file_only else "local (file)"
    if agent_name:
        logging.log(actual_log_level, f"{level_name} logging enabled for {agent_name} agent ({mode})")
    else:
        logging.log(actual_log_level, f"{level_name} logging enabled for ADK agent ({mode})")


def ensure_debug_logging(
    agent_name: Optional[str] = None, 
    log_level: Union[str, int, None] = None,
    cloud_mode: Optional[bool] = None
) -> None:
    """
    Ensure logging is maintained after agent creation.
    
    ADK might reset logging, so this function re-applies logging configuration.
    Call this after creating your agent to ensure logging stays at the configured level.
    
    Args:
        agent_name: Optional name of the agent (for logging identification)
        log_level: Logging level as string ("DEBUG", "INFO") or int. 
                  If None, uses same logic as setup_adk_logging (env var or default)
    
    Example:
        >>> from utility.logging_config import ensure_debug_logging
        >>> root_agent = Agent(...)
        >>> ensure_debug_logging(agent_name="MyAgent")
        >>> # Or with explicit level
        >>> ensure_debug_logging(agent_name="MyAgent", log_level="INFO")
    """
    setup_adk_logging(agent_name=agent_name, log_level=log_level, cloud_mode=cloud_mode)
    actual_log_level = _get_log_level(log_level)
    level_name = logging.getLevelName(actual_log_level)
    logging.log(actual_log_level, f"{level_name} logging re-verified after agent creation")

