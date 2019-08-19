import datetime
import logging
import threading

import colorama
from colorama import Back, Fore, Style

colorama.init()


class MyLogFormatter(logging.Formatter):
    """More colorful formatting with time and thread"""

    # No coverage because the unittest doesn't seem to execute the colorama stuff
    def format(record):  # pragma: no cover
        out_string = ""
        if record.levelname == logging.DEBUG:
            out_string += Fore.CYAN
        elif record.levelname == logging.INFO:
            out_string += ""
        elif record.levelname == logging.WARNING:
            out_string += Fore.YELLOW + Style.BRIGHT
        elif record.levelname == logging.ERROR:
            out_string += Fore.RED + Style.BRIGHT
        elif record.levelname == logging.CRITICAL:
            out_string += Fore.CYAN + Style.BRIGHT + Back.RED
        out_string += "[" + datetime.datetime.now().strftime("%H:%M:%S") + " " + threading.current_thread().name + " " + record.levelname + "]"
        out_string += Style.RESET_ALL
        out_string += "  "
        out_string += record.getMessage()
        return out_string


logger = logging.getLogger("MIDIEvents")
logger.setLevel("INFO")
sh = logging.StreamHandler()
sh.setFormatter(MyLogFormatter)
logger.addHandler(sh)
