import logging

# Try to import rich, but make it optional
try:
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.pretty import Pretty
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Create dummy classes if rich is not available
    class RichHandler(logging.StreamHandler):
        def __init__(self, *args, **kwargs):
            super().__init__()
    class Panel:
        def __init__(self, *args, **kwargs):
            pass
    class Console:
        def print(self, *args, **kwargs):
            pass

# Define custom logger levels with emojis
LOG_LEVELS = {
    "DEBUG": "🐛",
    "INFO": "✨",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
    "TOOL": "🤖",
}


class EmojiRichHandler(RichHandler):
    def get_level_text(self, record):
        level_emoji = LOG_LEVELS.get(record.levelname, "➡️")
        return f"[{record.levelname}] {level_emoji}"


# Configure the logger
logger = logging.getLogger("dlai")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    if RICH_AVAILABLE:
        handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            show_time=False,
            show_level=True,
            markup=False,
        )
    else:
        # Fallback to basic StreamHandler if rich is not available
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)

if RICH_AVAILABLE:
    console = Console()
else:
    console = None


def get_logger(name=None):
    """
    Returns a logger instance with the specified name.
    The logger is configured to use the EmojiRichHandler.
    """
    return logging.getLogger(name if name else "loop")


def log_tool_call(tool_name, args_str, result):
    """
    Logs a tool call with a card-like display.
    """
    MAX_DISPLAY_LENGTH = 200

    result_str = str(result)

    # Truncate if too long
    if len(args_str) > MAX_DISPLAY_LENGTH:
        args_str = args_str[:MAX_DISPLAY_LENGTH] + "..."
    if len(result_str) > MAX_DISPLAY_LENGTH:
        result_str = result_str[:MAX_DISPLAY_LENGTH] + "..."

    if RICH_AVAILABLE and console:
        panel_content = f"[bold]{tool_name}[/bold]\n"
        panel_content += f"Arguments: [cyan]{args_str}[/cyan]\n"
        panel_content += f"Result: [magenta]{result_str}[/magenta]"
        console.print(
            Panel(panel_content, title=f"{LOG_LEVELS['TOOL']} Tool Call", expand=False)
        )
    else:
        # Fallback to simple logging if rich is not available
        logger.info(f"Tool Call: {tool_name}")
        logger.info(f"  Arguments: {args_str}")
        logger.info(f"  Result: {result_str}")


# Example usage (optional, for testing)
if __name__ == "__main__":
    logger = get_logger()
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.debug("This is a debug message (won't show by default).")
    logging.getLogger("loop").setLevel(logging.DEBUG)
    logger.debug("This is a debug message (will show now).")
    log_tool_call("get_current_weather", {"city": "London"}, {"temp": "10C"})
