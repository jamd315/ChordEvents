import datetime
import logging
import threading

import colorama
from colorama import Back, Fore, Style

colorama.init()


class ChordEventsLogFormatter(logging.Formatter):  # TODO I'm not sure if this goes in __init__, but it works for now.
    """More colorful formatting with time and thread"""
    def format(record):
        outstr = ""
        if record.levelno < 10:          # NOTSET
            outstr += Fore.CYAN
        elif 10 <= record.levelno < 20:  # DEBUG
            outstr += Fore.CYAN
        elif 20 <= record.levelno < 30:  # INFO
            outstr += ""
        elif 30 <= record.levelno < 40:  # WARNING
            outstr += Fore.YELLOW + Style.BRIGHT
        elif 40 <= record.levelno < 50:  # ERROR
            outstr += Fore.RED + Style.BRIGHT
        elif 50 <= record.levelno:       # CRITICAL
            outstr += Fore.CYAN + Style.BRIGHT + Back.RED
        outstr += "[" + datetime.datetime.now().strftime("%H:%M:%S") + " " + threading.current_thread().name + " " + record.levelname + "]"
        outstr += Style.RESET_ALL
        outstr += "  "
        outstr += record.getMessage()
        return outstr


logger = logging.getLogger("ChordEvents")
logger.setLevel("INFO")
sh = logging.StreamHandler()
sh.setFormatter(ChordEventsLogFormatter)
logger.addHandler(sh)
