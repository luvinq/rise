import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<c>[ {extra[tag]} ]</c> <fg #808080>[ {time:HH:mm} ]</fg #808080> <level>[ {level} ]</level> <level>{message}</level>",
    colorize=True,
)
