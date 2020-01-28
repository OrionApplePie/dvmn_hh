import os

from dotenv import load_dotenv
import requests

load_dotenv()


AUTH_BY_PASSWORD_URL = "https://api.superjob.ru/2.0/oauth2/password/"
VACANCIES_SEARCH_URL = "https://api.superjob.ru/2.0/vacancies/"


def main():
    # load_dotenv()

    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    app_id = os.getenv("APP_ID")
    login = os.getenv("LOGIN")
    passwd = os.getenv("PASSWORD")

    params = {
        "login": login,
        "password": passwd,
        "client_id": app_id,
        "client_secret": secret_key,
        "hr": 0,
    }

    resp = requests.get(url=AUTH_BY_PASSWORD_URL, params=params)
    resp = resp.json()

    access_token = resp["access_token"]
    print(access_token[3:])

    headers = {
        "X-Api-App-Id": secret_key,
        # "Authorization": "Bearer " + access_token[3:]
    }

    vacancies = requests.get(url=VACANCIES_SEARCH_URL, headers=headers)
    print(vacancies.json())


if __name__ == "__main__":
    main()
