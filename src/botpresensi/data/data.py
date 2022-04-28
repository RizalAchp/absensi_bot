import json
import time
from datetime import datetime
from json.decoder import JSONDecodeError
from os import path
from types import ModuleType
from typing import Any

from colorama import Back, Fore, Style
from colorama.initialise import init

BASE_URL = "http://jti.polije.ac.id/elearning/"
URL_LOGIN = BASE_URL+"login"
URL_DASHBOARD = BASE_URL+"my"
URL_COURSES = "http://jti.polije.ac.id/elearning/course/index.php?categoryid=3"
# HEADERS = {
#     "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36")
# }
SETTING_MATKUL = path.abspath("config/list-matkul.json")
SETTING_USER = path.abspath("config/user.json")
ERROR = 1
WARNING = 2
INFO = 3
TIME = 5
E_MODE = f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}[ERROR]:{Back.RESET}{Fore.RED}"
W_MODE = f"{Fore.BLACK}{Back.YELLOW}{Style.BRIGHT}[WARNING]:{Back.RESET}{Fore.YELLOW}"
I_MODE = f"{Fore.BLACK}{Back.GREEN}{Style.BRIGHT}[INFO]:{Back.RESET}{Fore.GREEN}"
T_MODE = f"{Fore.BLACK}{Back.CYAN}{Style.BRIGHT}[TIMER]:{Back.RESET}{Fore.CYAN}"
N_MODE = f"{Fore.LIGHTGREEN_EX}{Style.DIM}"


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


class TheJson:
    def __init__(self, file: str) -> None:
        self.file = file

    def m_write(self, _d: dict):
        with open(self.file, 'w') as f:
            json.dump(_d, f, indent=4)
            f.close()

    def m_read(self):
        with open(self.file) as f:
            _jsn = json.load(f)
            f.close()
            return _jsn

    def check_data(self):
        try:
            with open(self.file) as f:
                json.load(f)
                f.close()
            return True
        except JSONDecodeError:
            return False


class MatkulSetting(TheJson):
    def __init__(self) -> None:
        super().__init__(SETTING_MATKUL)
        self.thedata = {}

    def get_link_from_date(self, name: datetime):
        return [
            Absensi(key, val, _link)
            for key, val in self.m_read().items()
            for _link in val
            if name.strftime('%a %-I%p') in key
        ]

    def add_matkul(self, name: str, lt: dict):
        self.thedata[name] = lt

    @property
    def data(self):
        return self.m_read()

    @data.setter
    def data(self, data: dict):
        self.thedata = data

    def submit_matkul(self):
        return self.m_write(self.thedata)


class CredSetting(TheJson):
    PRODI = ["1. THH", "2. MIF", "3. TIF"]

    def __init__(self) -> None:
        super().__init__(SETTING_USER)

    def get(self) -> Credentials:
        return Credentials(**self.m_read())

    def add(self, data: Credentials):
        self.data = vars(data)

    def submit(self):
        return self.m_write(self.data)

    def createNewAccount(self):
        """notify."""
        try:
            LOG(INFO, "\n\nSetting Akun JTI:")
            LOG(None, "Masukkan Informasi Dibawah sesuai akun JTI\n")

            nim = input("   NIM         : ")
            pswd = input("   PASSWORD    : ")

            LOG(None)
            LOG(None, "pilih Prodi anda: ")
            LOG(None, "===============")
            for i in self.PRODI:
                LOG(None, i)
            LOG(None, "\nKetikkan Prodi, Usahakan Sama Dengan List Diatas")
            LOG(None, "eg: not case sensitive")
            prodi = input("     prodi: ")
            LOG(None, "\nMasukkan juga golongan anda:")
            gol = input("   golongan: ")
            LOG(None, "\nMasukkan juga semester tempuh anda:")
            smstr = input("   semester: ")

            self.add(Credentials(
                nim.lower(), pswd, prodi.lower(), gol.upper(), smstr
            ))
            LOG(
                INFO,
                f"\n\nSubmitting akun, pada file {self.file}"
            )
            self.submit()
        except JSONDecodeError as e:
            LOG(ERROR, f"\nTERJADI MASALAH SAAT MEMBUAT AKUN: {e}")


class DataGui():
    """DataTabel."""
    PRODI = ["TKK", "MIF", "TIF"]
    GOL = ["A", "B", "C", "D"]
    idx_prodi = 0
    idx_gol = 0

    def __init__(self) -> None:
        """__init__.

        :param _httpget:
        :type _httpget: bool
        :param _url:
        :type _url: str
        :rtype: None
        """
        self.cred = CredSetting()
        self.mktl = MatkulSetting()
        try:
            __mtkl = self.mktl.data
            self._creds = self.cred.get()
            self._matkul = [DataMatkul(_d, _k) for _d, _k in __mtkl.items()]
        except JSONDecodeError:
            return None

    def set_cred(self):
        self.cred.add(self._creds)
        self.cred.submit()

    @property
    def credential(self) -> Credentials:
        return self._creds

    @credential.setter
    def credential(self, data: Credentials):
        self._creds = data

    @property
    def matkul(self):
        return self._matkul


class CompGui:
    """Components."""

    def __init__(self, imgui) -> None:
        """__init__.

        :rtype: None
        """
        self.imgui: Any = imgui
        self.w = 0
        self.h = 0
        self.fontb = None
        self.fontn = None
        self.lanjut = False

    @property
    def windowsize(self):
        return self.w, self.h

    @windowsize.setter
    def windowsize(self, d: tuple[int, int]):
        self.w, self.h = d

    @property
    def flags(self):
        return (
            self.imgui.WINDOW_NO_RESIZE |
            self.imgui.WINDOW_NO_MOVE |
            self.imgui.WINDOW_NO_COLLAPSE |
            self.imgui.WINDOW_MENU_BAR
        )


if __name__ == "__main__":
    LOG("INI ERROR COK", logmode=ERROR)
    LOG("INI WARNING COK", logmode=WARNING)
    LOG("INI INFO COK", logmode=INFO)
    LOG("INI DEFAULT COK")
    # matkul = MatkulSetting()
    # date = "Mon 1PM"
    # datas = datetime.strptime(date, "%a %I%p")
    # d = matkul.get_link_from_date(datas)
    # print(d)
    # if d:
    #     print("ada")
    # else:
    #     print("kososng")
