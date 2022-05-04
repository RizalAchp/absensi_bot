# Bot Scraping and Presensi Automatis JTI Polije

**status: alpha**

**Docker Image: https://hub.docker.com/r/rizalachp/botpresen-jti**

#### catatan:

- bot ini di buat khusus dijalanakan pada docker container
- upayakan di deploy pada cloud atau server anda sendiri menggunakan container docker

#### TODO

- memberikan notifikasi pada saat waktu presensi, sesuai dengan status presensi (discord? telegram? well..)
- optimasi :v
- testing :v

## Setup Awal

1.  pastikan anda mempunyai docker pada host, [info selengkapnya installasi docker](https://docs.docker.com)
2.  pastikan juga anda memiliki `docker-compose` juga [info selengkapnya installasi compose](https://docs.docker.com/compose/install/)
3.  jalankan container menggunakan command:

    ```bash
    sudo docker-compose run bot
    ```

    _otomatis docker compose akan build image dan menjalankan setup pada bot_

4.  enjoy!

    **alternatif:**

    - jalankan container docker menggunakan command: `sudo docker-compose up -d`
    - dan masuk pada container menggunakan command: `sudo docker exec -it BotPresensiJTI /bin/bash`
    - WORKDIR terdapat pada `/bot`
    - anda dapat menjalankan setup secara manual menggunakan command: `/bot/botpresen setup`
    - anda dapat menjalankan crontab secara manual menggunakan command: `/bot/botpresen cron`
    - argument command selengkapnya dapat dilihat menggunakan command: `/bot/botpresen -h`

      - output:

    ```
    usage: botpresent [-h, --help, arguments]

    Bot Scraping Pada JTI POLIJE menggunakan python

    positional arguments:
      argument:

            start     -> starting the bot(cli mode)
            gui       -> start bot(gui mode)
            cron      -> set cronjob
            setup     -> set user,link,etc..

    options:
      -h, --help            show this help message and exit

    by: Rizal Achmad Pahlevi
    ```

    - untuk `gui` tidak terimplementasi!

    - enjoy!

## Cara Kerja

- saat bagian setup awal, bot men-scraping web jti untuk mendapatkan informasi `url`, `waktu presensi`, dll..
- menggunakan `crontab` sebagai scheduling system yang menjalankan `executeable bot` pada waktu yang telah didapat pada saat setup
- crontab akan menjalankan command `/bot/botpresen start` yang memeriksa link pada waktu saat itu juga. dan memeriksa apakah terdapat presensi atau tidak
- jika terdapat presensi, bot akan POST data pada link presensi tersebut
- insya'allah script sudah saya optimasi sepenuhnya :v
