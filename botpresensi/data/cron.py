from datetime import datetime


class Cron:
    FIRST = [
        'SHELL=/bin/bash\n',
        'PATH=/sbin:/bin:/usr/sbin:/usr/bin\n',
        'MAILTO=""\n'
    ]
    COMMAND = "root run-parts /bot/botpresen start > /dev/null 2>&1"
    FILENAME = "/bot/crontab"

    def __init__(self) -> None:
        self.date = []

    def write(self):
        with open(self.FILENAME, 'w') as file:
            file.writelines(self.FIRST)
            file.write('\n')
            file.writelines(
                [f"{self._parse_cron(_dt)} {self.COMMAND}\n"
                 for _dt in self.date]
            )
            file.write('\n')

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
