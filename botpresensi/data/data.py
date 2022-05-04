from .model import *
from .cron import *


class TheJson:
    def __init__(self, file: str) -> None:
        if not path.exists(file):
            with open(file, 'x') as f:
                f.close()
        self.file = file

    def m_write(self, _d: dict):
        with open(self.file, 'w') as f:
            json.dump(_d, f, indent=4)
            f.close()

    def m_read(self):
        with open(self.file, 'r') as f:
            _jsn = json.load(f)
            f.close()
            return _jsn

    def check_data(self):
        return True if os.stat(self.file).st_size > 0 else False


class MatkulSetting(TheJson):
    def __init__(self) -> None:
        super().__init__(SETTING_MATKUL)
        self.thedata = {}

    def get_link_from_date(self, name: datetime):
        return [
            Absensi(key, _tgl, _link)
            for key, val in self.m_read().items()
            for _tgl, _link in val.items()
            if re.search(f"^{parse_date(name)}.*", _link)
            is not None
        ]

    def delete_link_done(self, _absn: Absensi):
        for key, val in self.m_read().items():
            for _k, _v in val.items():
                if key in _absn.name and _k in _absn.tgl:
                    continue
                self.thedata[key][_k] = _v

        return self.submit_matkul()

    def add_matkul(self, name: str, lt: dict):
        self.thedata[name] = lt

    def submit_matkul(self):
        return self.m_write(self.thedata)

    @property
    def data(self):
        return self.m_read()

    @data.setter
    def data(self, data: dict):
        self.thedata = data


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

            nim = input("   NIM         : ").lower()
            pswd = input("   PASSWORD    : ")

            LOG(None)
            LOG(None, "pilih Prodi anda: ")
            LOG(None, "===============")
            for i in self.PRODI:
                LOG(None, i)
            LOG(None, "\nKetikkan Prodi, Usahakan Sama Dengan List Diatas..")
            LOG(None, "`eg: not case sensitive`")
            prodi = input("\tprodi\t: ").upper()
            LOG(None, "\nMasukkan juga golongan anda..")
            gol = input("\tgol\t: ").upper()
            LOG(None, "\nMasukkan juga semester tempuh anda..")
            smstr = input("\tsmster\t: ")

            self.add(Credentials(
                nim, pswd, prodi, gol, smstr
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
        mktl = MatkulSetting()
        try:
            self._creds = self.cred.get()
            self._matkul = [DataMatkul(_d, _k)
                            for _d, _k in mktl.data.items()]
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

    def __init__(self, imgui: ModuleType) -> None:
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
    d = None
    if d:
        for _d in d:
            print(_d.link)
    else:
        print("None")
