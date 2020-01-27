import os

from dotenv import load_dotenv
import requests

SUPERJOB_API_URL = "https://api.superjob.ru/2.0/user/current/"

AUTHORIZATION_URL = "https://www.superjob.ru/authorize/"
ACCESS_TOKEN_API = "https://api.superjob.ru/2.0/oauth2/access_token/"

AUTH_BY_PASSWORD_URL = "https://api.superjob.ru/2.0/oauth2/password/"


def main():
    load_dotenv()

    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    app_id = os.getenv("APP_ID")
    login = os.getenv("LOGIN")
    passwd = os.getenv("PASSWORD")

    headers = {"X-Api-App-Id": secret_key, "X-User-Type": "reg_user"}

    params = {
        "login": login,
        "password": passwd,
        "client_id": app_id,
        "client_secret": secret_key,
        "hr": 0,
    }

    resp = requests.get(url=AUTH_BY_PASSWORD_URL, params=params)
    print(resp.text)


if __name__ == "__main__":
    main()
