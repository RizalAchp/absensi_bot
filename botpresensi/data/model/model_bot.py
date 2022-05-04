from os import path
from datetime import datetime
from types import ModuleType
import time
from json.decoder import JSONDecodeError
import json
import re
import os
from typing import Any
import shutil

from colorama import Back, Fore, Style
from colorama.initialise import init

BASE_URL = "http://jti.polije.ac.id/elearning/"
URL_LOGIN = BASE_URL+"login"
URL_DASHBOARD = BASE_URL+"my/index.php?myoverviewtab=courses"
URL_COURSES = "http://jti.polije.ac.id/elearning/course/index.php?categoryid=3"
# HEADERS = {
#     "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36")
# }
SETTING_MATKUL = "/usr/src/bot/list-matkul.json"
SETTING_USER = "/usr/src/bot/user.json"
ERROR = 1
WARNING = 2
INFO = 3
TIME = 5
E_MODE = f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}[ERROR]:{Back.RESET}{Fore.RED}"
W_MODE = f"{Fore.BLACK}{Back.YELLOW}{Style.BRIGHT}[WARNING]:{Back.RESET}{Fore.YELLOW}"
I_MODE = f"{Fore.BLACK}{Back.GREEN}{Style.BRIGHT}[INFO]:{Back.RESET}{Fore.GREEN}"
T_MODE = f"{Fore.BLACK}{Back.CYAN}{Style.BRIGHT}[TIMER]:{Back.RESET}{Fore.CYAN}"
N_MODE = f"{Fore.LIGHTGREEN_EX}{Style.DIM}"


def parse_date(_date: str | datetime):
    if isinstance(_date, datetime):
        return _date.strftime('%a %d %b %Y %-I%p')
    return datetime.strptime(
        _date.split(' - ')[0], '%a %d %b %Y %I%p'
    )


def LOG(*val: object,
        sep: str | None = None,
        logmode: int | None = None
        ) -> None:
    init()
    if logmode == ERROR:
        return print(E_MODE, *val, Style.RESET_ALL)
    elif logmode == WARNING:
        return print(W_MODE, *val, Style.RESET_ALL)
    elif logmode == INFO:
        return print(I_MODE, *val, Style.RESET_ALL)
    elif logmode == TIME:
        return print(T_MODE, *val, Style.RESET_ALL)
    else:
        return print(N_MODE, *val, Style.RESET_ALL)


def mytimer(fun):
    async def wrapper(*args, **kwargs):
        _st = time.time()
        _f = await fun(*args, **kwargs)
        LOG(
            f'Func {fun.__name__!r} executed in {(time.time() - _st):.3f}s',
            logmode=TIME
        )
        return _f
    return wrapper


class Credentials:
    def __init__(self, nim: str, pswd: str,
                 prodi: str, gol: str, smstr: str):
        self.nim = nim
        self.pswd = pswd
        self.prodi = prodi
        self.gol = gol
        self.smstr = smstr


class DataMatkul:
    def __init__(self, name: str, data: dict) -> None:
        self.name = name
        self.data = data


class Absensi:
    def __init__(self, name: str, tgl: str, link: str) -> None:
        self.name = name
        self.tgl = tgl
        self.link = link
