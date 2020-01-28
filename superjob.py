import os
import datetime

from dotenv import load_dotenv, find_dotenv
import requests


AUTH_BY_PASSWORD_URL = "https://api.superjob.ru/2.0/oauth2/password/"
VACANCIES_SEARCH_URL = "https://api.superjob.ru/2.0/vacancies/"
MOSKOW_CITY_ID = 4


def main():
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
    print(access_token)

    headers = {
        "X-Api-App-Id": secret_key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + access_token[3:],
    }
    month_ago_date = datetime.datetime.now() - datetime.timedelta(days=30)

    params_vac = {
        "town": MOSKOW_CITY_ID,
        "date_published_from": month_ago_date,
        "keyword": "программист",
        # "page": 1,
        # "count": 100,
    }
    vacancies = requests.get(
        url=VACANCIES_SEARCH_URL, headers=headers, params=params_vac
    )
    res = vacancies.json()

    print(len(res["objects"]))

    for item in res["objects"]:
        print("--> {0}, {1}".format(item["id"], item["profession"]))


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
