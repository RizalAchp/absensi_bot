import asyncio
import re
import aiohttp

from bs4 import BeautifulSoup

from botpresensi import (
    ERROR, INFO, LOG, URL_COURSES,
    URL_LOGIN, CredSetting, Cron,
    JSONDecodeError, MatkulSetting,
    datetime, mytimer
)
from botpresensi.data.data import SETTING_MATKUL, SETTING_USER


class Bot():
    """Bot."""

    VERSION = 1.0
    AUTHOR = "Rizal Achmad Pahlevi"

    def __init__(self, session: aiohttp.ClientSession):
        """__init__.

        :param session:
        :type session: aiohttp.ClientSession
        :rtype: None
        """

        LOG("<=== BOT BERJALAN ===>", logmode=INFO)
        LOG(f"VERSION   : {self.VERSION}", logmode=INFO)
        LOG(f"AUTHOR    : {self.AUTHOR}", logmode=INFO)

        self.sesn = session
        bot_cred = CredSetting()
        self.status_login = False

        try:
            LOG("Check akun..", logmode=INFO)
            bot_data = bot_cred.get()
            self.bot_data_payload = {
                'username': bot_data.nim,
                'password': bot_data.pswd
            }
            self.prodi = bot_data.prodi
            self.gol = bot_data.gol
            self.smstr = bot_data.smstr
            self.status_login = True

        except JSONDecodeError:
            LOG("Akun belum ada, Memulai Proses Untuk Menyimpan akun Baru..",
                logmode=INFO)

    @mytimer
    async def bot_login(self, setup: bool = False):
        """bot_login.

        :param setup:
        :type setup: bool
        """
        async with self.sesn.get(URL_LOGIN) as resp:
            LOG(f"Mencoba Mengunjungi Url:{URL_LOGIN}", logmode=INFO)

            http = await resp.text()
            self.bot_data_payload['logintoken'] = self.get_authenticity_token(
                http
            )

            LOG("Mendapatkan Payload `logintoken`: "
                f"{self.bot_data_payload['logintoken']}",
                logmode=INFO)

        post_login = URL_LOGIN+"/index.php"
        async with self.sesn.post(
            post_login, data=self.bot_data_payload
        ) as resplgn:
            LOG(f'cookies : {resplgn.cookies.output()}')

            if resplgn.status in (200, 303):
                if setup is True:
                    return LOG(f"Mode Setup :{setup}", logmode=INFO)
                return LOG("berhasil login", logmode=INFO)
            return LOG(
                "terjadi kegagalan dalam login..\
                \ndimohon untuk mencoba kembali..",
                logmode=ERROR
            )

    @mytimer
    async def bot_absen(self):
        """bot_absen. """
        payload_absen = {
            "_qf_mod_attendance_student_attendance_form": 1,
            "mform_isexpanded_id_session": 1,
            "submitbutton": "Save changes"
        }
        _link = await self.bot_check_absen_link()
        if _link:
            for link in _link:
                _ln, _dt = self.striplink(link)
                payload_absen["sessid"] = self.get_sessid(_dt)
                payload_absen["sesskey"] = self.get_sesskey(_dt)
                async with self.sesn.get(link) as resp:
                    html = await resp.text()
                    payload_absen["status"] = self.get_status(html)

                async with self.sesn.post(_ln, data=payload_absen) as resp:
                    pass
            return True
        return False

    @mytimer
    async def bot_check_absen_link(self) -> list[str] | None:
        """bot_check_absen."""
        _data = MatkulSetting().get_link_from_date(datetime.now())
        data = []
        if _data:
            for _v in _data:
                async with self.sesn.get(_v.link) as resp:
                    html = await resp.text()
                    for result in BeautifulSoup(
                        html, "html.parser"
                    ).find_all('a', text=re.compile("^Submi.*dance.*")):
                        data.append(result.get('href'))

            return data
        return None

    @mytimer
    async def bot_settingdata(self, _data: dict[str, list]) -> None:
        """bot_settingdata.

        :param _data:
        :type _data: dict[str, list]
        """
        LOG("Memasuki mode setup..", logmode=INFO)
        matkul = MatkulSetting()

        for _d, _v in _data.items():
            for link in _v:
                tglnlink = await self.bot_get_tgl(link)
                matkul.add_matkul(_d, tglnlink)
                LOG(f"mendapatkan data : {tglnlink}")

        return matkul.submit_matkul()

    @mytimer
    async def bot_get_presensi_url(
        self, _matkul: dict
    ) -> dict[str, list[str]]:
        """bot_geturl.

        :param _matkul:
        :type _matkul: dict
        """
        LOG("scraping pada setuap matkul untuk mendapatkan link presensi",
            logmode=INFO)

        url: dict[str, list] = {}
        for key in _matkul:
            url[key] = await self._getlinkpresen(key, _matkul[key])

        return url

    @mytimer
    async def bot_get_tgl(self, url: str) -> dict[str, str]:
        """_get_tgl.

        :param url:
        :type url: str
        """
        async with self.sesn.get(url+"&view=5") as _resp:
            LOG("scraping data tanggal dan link presensi", logmode=INFO)
            LOG(f"url : {url}")
            html = await _resp.text()
            _tr = BeautifulSoup(
                html, "html.parser"
            ).find(
                'table', {'class': re.compile("^generaltab.*")}
            ).find('tbody').find_all('tr')
            _resp.close()

            return {
                _col.select_one(
                    ".datecol.cell.c0"
                ).get_text(): url for _col in _tr if re.search(
                    r"\A\?", _col.select_one(
                        ".statuscol.cell.c2"
                    ).get_text()
                ) is not None
            }

    @mytimer
    async def _getlinkpresen(self, name, url) -> list[str]:
        """_getlinkpresen.

        :param name:
        :param url:
        """
        LOG(f"memasuki link matkul : {name} -> {url}", logmode=INFO)
        async with self.sesn.get(url) as _resp:
            html = await _resp.text()
            elem = BeautifulSoup(
                html, "html.parser"
            ).find_all('a', {'href': re.compile(
                "^http.*/mod/attendance/.*"
            )})
            _resp.close()
            return [
                prns.get('href') for prns in elem
                if re.search(
                    f"^Pres.*Kuliah.*|^PRES.*{self.gol}.*|^Pres.*{self.gol}.*",
                    prns.get_text()
                ) is not None
            ]

    @mytimer
    async def link_matkul(self) -> dict[str, str]:
        """link_matkul."""
        LOG("scraping data_url matakuliah..")

        async with self.sesn.get(URL_COURSES) as resp:
            html = await resp.text()
            _data = {
                str(e.get('href')): str(e.text) for e in BeautifulSoup(
                    html, "html.parser"
                ).find_all(
                    'a', text=re.compile(
                        f"^{self.prodi+self.smstr}.*"
                    )
                )
            }
            resp.close()
            return {
                _val: _key for _key, _val in _data.items()
            }

    @staticmethod
    def check_setting_bot():
        setting = MatkulSetting()
        return setting.check_data()

    @staticmethod
    def get_authenticity_token(html: str) -> str:
        """get_authenticity_token.

        :param html:
        :type html: str
        """
        token = BeautifulSoup(
            html, "html.parser"
        ).find('input', attrs={'name': 'logintoken'})
        return token.get('value').strip()

    @staticmethod
    def striplink(link: str):
        _d = link.split("?")
        return (_d[0], _d[1])

    @staticmethod
    def get_sessid(link: str) -> str:
        data = re.search("sessid=([0-9a-zA-Z]+)&?", link)
        if data:
            return str(data.group(1))
        return ""

    @staticmethod
    def get_sesskey(link: str) -> str:
        data = re.search("sesskey=([0-9a-zA-Z]+)&?", link)
        if data:
            return str(data.group(1))
        return ""

    @staticmethod
    def get_status(html: str) -> str:
        elem = BeautifulSoup(
            html, "html.parser"
        ).find('input', attrs={'name': 'status'})
        return elem.get('value').strip()


@mytimer
async def set_crontab():
    """Set Contab Setting"""
    _d = MatkulSetting()
    _cr = Cron()
    for val in _d.data:
        _cr.set_contab_list(list(_d.data[val]))
    _cr.write()
    LOG(f"writing cronjob to {_cr.FILENAME!r}", logmode=INFO)
    return True


async def setting_up(bot: Bot):
    """Setting Up Bot"""
    await bot.bot_login(True)
    link_matkul = await bot.link_matkul()
    linkget = await bot.bot_get_presensi_url(link_matkul)
    if linkget:
        await bot.bot_settingdata(linkget)
        LOG("mendapatkan keseluruhan data", logmode=INFO)
        isdone = await set_crontab()
        return isdone


async def setupbot():
    """setupbot."""
    global IS_DONE
    IS_DONE = False
    async with aiohttp.ClientSession() as req:
        bot = Bot(req)
        if bot.status_login:
            if bot.check_setting_bot() is False:
                IS_DONE = await setting_up(bot)
            else:
                LOG("sudah melakukan setting data, jika ingin resetting..")
                LOG(f"hapus data pada : {SETTING_MATKUL}")
                LOG("dan jalankan kembali script setup..")
        else:
            cred = CredSetting()
            cred.createNewAccount()
            IS_DONE = await setting_up(bot)
        await req.close()

    if IS_DONE:
        LOG("SETUP SELESAI", logmode=INFO)
        LOG("configurasi setup terdapat pada :", logmode=INFO)
        LOG(f"  config matkul : {SETTING_MATKUL}", logmode=INFO)
        LOG(f"  config user   : {SETTING_USER}", logmode=INFO)


async def startwithcli():
    """Menjalankan Bot."""
    global IS_DONE
    IS_DONE = False
    async with aiohttp.ClientSession() as req:
        bot = Bot(req)
        if bot.status_login:
            await bot.bot_login()
            if bot.check_setting_bot() is True:
                IS_DONE = await bot.bot_absen()

            else:
                IS_DONE = await setting_up(bot)

        else:
            cred = CredSetting()
            cred.createNewAccount()
            IS_DONE = await setting_up(bot)
        await req.close()

    if IS_DONE:
        LOG("ABSENSI SELESAI", logmode=INFO)
        LOG(f"pada : {datetime.now()}", logmode=INFO)


async def startCronjob():
    """startCronjob."""
    raise NotImplementedError(f"{startCronjob.__name__}")

if __name__ == "__main__":
    asyncio.run(set_crontab())
