import datetime as dt
import os
from itertools import count

import requests
from dotenv import find_dotenv, load_dotenv
from requests.compat import urljoin

SUPERJOB_AUTH_URL = "https://api.superjob.ru/2.0/oauth2/password/"
SUPERJOB_VACANCIES_SEARCH_URL = "https://api.superjob.ru/2.0/vacancies/"
SUPERJOB_MOSKOW_ID = 4
SUPERJOB_VACANCIES_PERIOD = 30

HH_API_BASE_URL = "https://api.hh.ru/"
HH_VACANCIES_PATH = "/vacancies"
HH_PROGRAMMER_SPEC_ID = "1.221"
HH_AREA_MOSCOW_CODE = "1"
HH_VACANCY_PERIOD = "30"

PROGRAMMING_LANGUAGES = (
    "JavaScript", "Java", "Python"
    # "Ruby", "PHP", "C++",
    # "C#", "Go", "Swift"
)


def get_vacancies_hh(search_text="", page=0):
    """Request to /vacancies API endpoint."""

    query_params = {
        "specialization": HH_PROGRAMMER_SPEC_ID,
        "area": HH_AREA_MOSCOW_CODE,
        "period": HH_VACANCY_PERIOD,

        "text": search_text,
        "page": page
    }

    url = urljoin(
        HH_API_BASE_URL, HH_VACANCIES_PATH
    )

    response = requests.get(
        url=url,
        params=query_params
    )
    response.raise_for_status()

    return response


def predict_salary(salary_from, salary_to):
    """Вычисление средней зарплаты по границам 'вилки'."""
    average_salary = 0

    if salary_from and salary_to:
        average_salary = (salary_from + salary_to) / 2

    if salary_from and not salary_to:
        average_salary = salary_from * 1.2

    if not salary_from and salary_to:
        average_salary = salary_to * 0.8

    return average_salary


def predict_rub_salary_hh(vacancy=None):
    """Calculate average salary of given hh vacancy
    or return None if no information of salary.
    Process only if currency is RUR."""

    salary = vacancy["salary"]

    if salary is None:
        return None

    if salary["currency"] != "RUR":
        return None

    salary_from = salary["from"]
    salary_to = salary["to"]

    return int(
        predict_salary(salary_from, salary_to)
    )

# TODO: нужна ли эта функция?
def get_vacancies_found_number_hh(search_text=""):
    """Get number of found vacancies by search text."""
    response = get_vacancies_hh(
        search_text=search_text,
    )
    response.raise_for_status()
    return int(
        response.json()["found"]
    )


def fetch_all_vacancies_hh(search_text="", start_page=0):
    """Fetch all vacancies from every pages. (API limit is 2000)."""
    for page in count(start_page):
        print(f"fetch by search text: {search_text}, page: {page}")
        response = get_vacancies_hh(
            search_text=search_text,
            page=page
        )
        response.raise_for_status()

        page_data = response.json()

        if page >= page_data["pages"] - 1:
            break

        yield from page_data["items"]


def calc_average_salary_language_hh(lang=""):
    """Caclculate average salary of vacancies by given language."""

    search_text = lang
    print(f"fetch {lang} vacancies...")  # fix me!!!
    vacancies_found = get_vacancies_found_number_hh(
        search_text=search_text
    )
    all_vacancies = fetch_all_vacancies_hh(
        search_text=search_text,
    )

    vacancies_with_salary = [
        predict_rub_salary_hh(vacancy)
        for vacancy in all_vacancies
        if predict_rub_salary_hh(vacancy) is not None
    ]
    average_salary = int(
        sum(vacancies_with_salary) / len(vacancies_with_salary)
    )

    return {
        f"{lang}": {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(vacancies_with_salary),
            "average_salary": average_salary
        }
    }


def fetch_all_vacancies_sj(search_text=""):
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    app_id = os.getenv("APP_ID")
    login = os.getenv("LOGIN")
    passwd = os.getenv("PASSWORD")

    auth_params = {
        "login": login,
        "password": passwd,
        "client_id": app_id,
        "client_secret": secret_key,
        "hr": 0,
    }

    resp = requests.get(url=SUPERJOB_AUTH_URL, params=auth_params)
    resp = resp.json()
    access_token = resp["access_token"]

    headers = {
        "X-Api-App-Id": secret_key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + access_token,
    }

    month_ago_date = dt.datetime.now() - dt.timedelta(days=SUPERJOB_VACANCIES_PERIOD)
    vacancies_params = {
        "town": SUPERJOB_MOSKOW_ID,
        "date_published_from": month_ago_date,
        "keyword": search_text,
        # "keywords": [[1, None, search_text], ],
        "catalogues": 48,
        "page": 5,
        "count": 100,
    }
    vacancies = requests.get(
        url=SUPERJOB_VACANCIES_SEARCH_URL,
        headers=headers,
        params=vacancies_params
    )
    # import ipdb; ipdb.set_trace()
    res = vacancies.json()
    # print(len(res["objects"]))
    # for item in res["objects"]:
    #     cat = ", ".join(
    #         map(lambda category: category["title"], item["catalogues"])
    #     )
    #     print("--> ({4} | {3}) {0}, {1} / город: {2}".format(
    #         item["id"], item["profession"],
    #         item["town"]["title"], item["firm_name"], 
    #         cat
    #     ))
    return res["objects"]


def predict_rub_salary_sj(vacancy=None):
    salary_from = vacancy["payment_from"]
    salary_to = vacancy["payment_to"]

    if salary_from == salary_to == 0:
        return None
    if not salary_from or not salary_to:
        return None

    return int(
        predict_salary(salary_from, salary_to)
    )


def calc_average_salary_language_sj(lang=""):
    search_text = lang

    vacancies = fetch_all_vacancies_sj(search_text)
    average_salary = 0
    processed_vacancies = 0

    vacancies_with_salary = [
        predict_rub_salary_sj(vacancy)
        for vacancy in vacancies
        if predict_rub_salary_sj(vacancy)
    ]

    average_salary = int(
        sum(vacancies_with_salary) / len(vacancies_with_salary)
    )

    return {
        f"{lang}": {
            "vacancies_found": len(vacancies),
            "vacancies_processed": len(vacancies_with_salary),
            "average_salary": average_salary
        }
    }


def main():
    # avg_salaries = []

    # for lang in PROGRAMMING_LANGUAGES:
    #     avg_salaries.append(
    #         calc_average_salary_language_hh(lang=lang)
    #     )

    # for lang_salary in avg_salaries:
    #     for name in lang_salary.keys():
    #         info = lang_salary[name]
    #         print(
    #             (f'{name} / found: {info["vacancies_found"]} /'
    #              f' processed: {info["vacancies_processed"]} /'
    #              f' avg salary: {info["average_salary"]} ')
    #         )
    python_vacancies = calc_average_salary_language_sj("Python")
    print(python_vacancies)


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
    # main_sj()