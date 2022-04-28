from typing import Text
from bs4.element import NavigableString, Tag
import requests
from bs4 import BeautifulSoup


def get_authenticity_token(html):
    soup = BeautifulSoup(html, "html.parser")
    token = soup.find('input', attrs={'name': 'logintoken'})
    if isinstance(token, Tag):
        return token.get('value').strip()
    print('could not find `authenticity_token` on login form')


def checkDasboard(html):
    soup = BeautifulSoup(html, "html.parser")
    token = soup.find_all('div', attrs={'class': 'courses'})
    print(f'chaeckdasboard{token}')
# payload = {'username': 'e32201406', 'password': 'Muhammad50546%)%$^'}

# s = session.post("http://jti.polije.ac.id/elearning/login", data=payload)

# print(s)


LOGIN_URL = "http://jti.polije.ac.id/elearning/login"
DASHBOARD = "http://jti.polije.ac.id/elearning/course/index.php?categoryid=3"

payload = {
    'username': "e32201406",
    'password': "Muhammad50546%)%$^",
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36"}
with requests.Session() as session:
    response = session.get(LOGIN_URL, headers=headers)
    print(f'url {response.url}\n')

    payload['logintoken'] = get_authenticity_token(response.text)
    print(f'payload {payload}\n')
    p = session.post(LOGIN_URL+"/index.php", data=payload,
                     headers=headers)  # perform login

    print(f'history {p.history}')
    print(f'url {p.url}')
    print(f'status_code {p.status_code}')
    print(f'is redirect {p.is_redirect}\n')

    resp = session.get(DASHBOARD)
    checkDasboard(resp.text)
    print(f'history {resp.history}')
    print(f'url {resp.url}')
    print(f'status_code {resp.status_code}')
    print(f'is redirect {resp.is_redirect}\n')

# s = session.get(DASHBOARD, headers=headers,
#                 allow_redirects=True)  # perform login
# checkDasboard(s.text)

# print(f'next {s.next.__repr__()}')
# print(f'url {s.links}')
# print(f'status_code {s.status_code}')
# print(f'is redirect {s.is_redirect}')
