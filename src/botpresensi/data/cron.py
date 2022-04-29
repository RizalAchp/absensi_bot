from datetime import datetime
import os


class Cron:
    ENCODING = "utf-8"

    def __init__(self) -> None:
        self.COMMAND = os.path.abspath("bin/runbot")
        self.FILENAME = os.path.abspath("src/crontab")
        self.date = []

    def write(self):
        with open(self.FILENAME, 'w') as file:
            for _dt in self.date:
                file.write(f"{self._parse_cron(_dt)} {self.COMMAND}\n")

            file.close()

    def set_contab_list(self,  _date: list):
        if _date:
            for _d in _date:
                self.date.append(self.parse_date(_d))

    def _parse_cron(self, _dt: datetime):
        return f"{5} {_dt.hour} * {_dt.month} {_dt.isoweekday()}"

    @staticmethod
    def parse_date(_date: str):
        return datetime.strptime(
            _date.split(' - ')[0], '%a %d %b %Y %I%p'
        ).astimezone()

    def run(self):
        pass


if __name__ == "__main__":
    cron = Cron()
    data = cron.parse_date("Mon 14 Feb 2022 1PM - 3PM")
    print("Mon 14 Feb 2022 1PM - 3PM")
    print(data)
    print(cron._parse_cron(data))
