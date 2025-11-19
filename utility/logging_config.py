"""
Logging configuration utility for ADK agents.

This module provides a reusable function to configure detailed DEBUG-level logging
for ADK agents, ensuring all logs go to file (not stdout/stderr).
"""

import logging
import os
from typing import Optional


def setup_adk_logging(
    agent_name: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: int = logging.DEBUG,
    file_only: bool = True
) -> None:
    """
    Configure detailed logging for ADK agents.
    
    This function sets up DEBUG-level logging to capture:
    - Events and traces
    - Request/Response details
    - Token usage information
    - Metadata and model interactions
    - HTTP request/response details
    
    Args:
        agent_name: Optional name of the agent (for logging identification)
        log_file: Optional path to log file. If None, uses ADK's default location.
        log_level: Logging level (default: logging.DEBUG)
        file_only: If True, removes stdout/stderr handlers (default: True)
    
    Example:
        >>> from utility.logging_config import setup_adk_logging
        >>> setup_adk_logging(agent_name="MyAgent")
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Determine log file location
    if log_file is None:
        # ADK creates log files in: %TEMP%\agents_log\agent.latest.log
        log_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'agents_log')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'agent.latest.log')
    
    # Remove all StreamHandlers (stdout/stderr) if file_only is True
    if file_only:
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)
            elif isinstance(handler, logging.FileHandler):
                # Remove any existing file handlers for the same file to avoid duplicates
                handler_path = getattr(handler, 'baseFilename', None) or getattr(
                    getattr(handler, 'stream', None), 'name', None
                )
                if handler_path and log_file in str(handler_path):
                    root_logger.removeHandler(handler)
    
    # Create and add file handler
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set DEBUG level for ADK and related modules explicitly
    loggers_to_debug = [
        'adk', 'google.adk', 'google_adk',
        'google.genai', 'google.genai.types', 'google.genai._client',
        'google.genai.models', 'google.genai.google_llm',
        'httpx', 'httpcore', 'urllib3'
    ]
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        if file_only:
            # Remove StreamHandlers from child loggers (only keep file handlers)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler):
                    logger.removeHandler(handler)
                elif isinstance(handler, logging.FileHandler):
                    handler.setLevel(log_level)
        
        # Propagate to root logger so file handler catches it
        logger.propagate = True
    
    # Ensure all root logger handlers are set correctly
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(log_level)
        elif file_only and not isinstance(handler, logging.FileHandler):
            # Remove any non-file handlers if file_only is True
            root_logger.removeHandler(handler)
    
    # Log that debug logging is enabled
    if agent_name:
        logging.debug(f"DEBUG logging enabled for {agent_name} agent")
    else:
        logging.debug("DEBUG logging enabled for ADK agent")


def ensure_debug_logging(agent_name: Optional[str] = None) -> None:
    """
    Ensure DEBUG logging is maintained after agent creation.
    
    ADK might reset logging, so this function re-applies DEBUG level configuration.
    Call this after creating your agent to ensure logging stays at DEBUG.
    
    Args:
        agent_name: Optional name of the agent (for logging identification)
    
    Example:
        >>> from utility.logging_config import ensure_debug_logging
        >>> root_agent = Agent(...)
        >>> ensure_debug_logging(agent_name="MyAgent")
    """
    setup_adk_logging(agent_name=agent_name, file_only=True)
    logging.debug("DEBUG logging re-verified after agent creation")

