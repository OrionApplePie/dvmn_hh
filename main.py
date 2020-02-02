import datetime as dt
import os
from itertools import count

import requests
from dotenv import find_dotenv, load_dotenv
from requests.compat import urljoin
from requests.exceptions import HTTPError
from terminaltables import AsciiTable

SUPERJOB_AUTH_URL = "https://api.superjob.ru/2.0/oauth2/password/"
SUPERJOB_VACANCIES_SEARCH_URL = "https://api.superjob.ru/2.0/vacancies/"
SUPERJOB_MOSKOW_ID = 4
SUPERJOB_VACANCIES_PERIOD = 30
SUPERJOB_CATALOG_CODE = 48

HH_API_BASE_URL = "https://api.hh.ru/"
HH_VACANCIES_PATH = "/vacancies"
HH_PROGRAMMER_SPEC_ID = "1.221"
HH_AREA_MOSCOW_CODE = "1"
HH_VACANCY_PERIOD = "30"

SEARCH_TEXT_PART = "Программист"
PROGRAMMING_LANGUAGES = (
    "JavaScript", "Java",
    "Python", "C",
    "Ruby", "PHP", "C++",
    "C#", "Go",
)


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


def calc_average_salary_all_languages(calc_func=None, languages=PROGRAMMING_LANGUAGES):
    """Сбор вакансий и вычисление средних зарплат
    по всем заданным в списке языкам программирования."""
    return [
        calc_func(lang=lang)
        for lang in languages
    ]


def get_vacancies_page_hh(search_text="", page=0):
    """Запрашивает /response API hh.ru и возвращает response вакансий страницы."""

    query_params = {
        "specialization": HH_PROGRAMMER_SPEC_ID,
        "area": HH_AREA_MOSCOW_CODE,
        "period": HH_VACANCY_PERIOD,
        "text": search_text,
        "page": page,
    }

    url = urljoin(HH_API_BASE_URL, HH_VACANCIES_PATH)

    response = requests.get(url=url, params=query_params)
    response.raise_for_status()

    return response


def fetch_all_vacancies_hh(search_text="", start_page=0):
    """Запрос всех вакансий по поисковому запросу с каждой страницы 
    (hh.ru, ограничение API - 2000 результатов)."""
    for page in count(start_page):
        response = get_vacancies_page_hh(search_text=search_text, page=page)

        page_data = response.json()

        if page >= page_data["pages"] - 1:
            break

        yield from page_data["items"]


def predict_rub_salary_hh(vacancy=None):
    """Вычисление средней зарплаты вакансии с hh.ru,
    возвращает None если нет информации о зарплате,
    обрабатывает только зарплаты в рублях RUR."""

    salary = vacancy["salary"]

    if salary is None:
        return None

    if salary["currency"] != "RUR":
        return None

    salary_from = salary["from"]
    salary_to = salary["to"]

    return int(predict_salary(salary_from, salary_to)) or None


def calc_average_salary_language_hh(lang=""):
    """Вычисление средней зарплаты по найденным вакансиям hh.ru из списка."""
    search_text = " ".join([SEARCH_TEXT_PART, lang])
    all_vacancies = fetch_all_vacancies_hh(search_text=search_text)

    predicted_data = [
        predict_rub_salary_hh(vacancy)
        for vacancy in all_vacancies
    ]
    predicted_salaries = list(filter(None, predicted_data))
    predicted_salaries_number = len(predicted_salaries)
    try:
        average_salary = int(
            sum(predicted_salaries) / predicted_salaries_number
        )
    except ZeroDivisionError:
        average_salary = 0

    return  [
        lang,
        get_vacancies_found_number_hh(search_text=search_text),
        predicted_salaries_number,
        average_salary
    ]


def get_vacancies_found_number_hh(search_text=""):
    """Число всех найденных по запросу вакансий hh.ru."""
    response = get_vacancies_page_hh(search_text=search_text)
    response.raise_for_status()
    return response.json()["found"]


def auth_sj():
    """Авторизация по логину и паролю на SuperJob. Возвращает Access token."""
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    app_id = os.getenv("SUPERJOB_APP_ID")
    login = os.getenv("SUPERJOB_LOGIN")
    passwd = os.getenv("SUPERJOB_PASSWORD")

    params = {
        "login": login,
        "password": passwd,
        "client_id": app_id,
        "client_secret": secret_key,
        "hr": 0,
    }
    response = requests.get(url=SUPERJOB_AUTH_URL, params=params)
    response.raise_for_status()

    return response.json()["access_token"]


def get_vacancies_page_sj(search_text="", page=0, count=100):
    """Запрашивает API SuperJob и возвращает response вакансий страницы."""
    access_token = auth_sj()
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")

    headers = {
        "X-Api-App-Id": secret_key,
        # "Content-Type": "application/x-www-form-urlencoded",  # TODO: нужно?
        "Authorization": "Bearer " + access_token,
    }
    month_ago_date = dt.datetime.now() - dt.timedelta(days=SUPERJOB_VACANCIES_PERIOD)

    params = {
        "town": SUPERJOB_MOSKOW_ID,
        "date_published_from": month_ago_date,
        "keyword": search_text,
        # "keywords": [[1, None, search_text], ],
        "catalogues": SUPERJOB_CATALOG_CODE,
        "page": page,
        "count": count,
    }
    page_response = requests.get(
        url=SUPERJOB_VACANCIES_SEARCH_URL, headers=headers, params=params
    )
    page_response.raise_for_status()
    return page_response


def get_vacancies_found_number_sj(search_text=""):
    """Число всех найденных по запросу вакансий SuperJob."""
    response = get_vacancies_page_sj(search_text=search_text)
    return response.json()["total"]


def fetch_all_vacancies_sj(search_text="", max_pages=5, vacancies_count=100):
    """Запрос всех вакансий по поисковому запросу с каждой старницы 
    (SuperJob, ограничение API - 500 результатов)."""
    for page in count(0):
        if page > max_pages - 1:
            break
        vacancies_page = get_vacancies_page_sj(
            search_text=search_text,
            page=page, count=vacancies_count
        )
        yield from vacancies_page.json()["objects"]


def predict_rub_salary_sj(vacancy=None):
    """Вычисление средней зарплаты вакансии с SuperJob,
    возвращает None если нет информации о зарплате,
    обрабатывает только зарплаты в рублях rub."""
    salary_from = vacancy["payment_from"]
    salary_to = vacancy["payment_to"]

    if not salary_from or not salary_to:
        return None
    if vacancy["currency"] != "rub":
        return None

    return int(predict_salary(salary_from, salary_to)) or None


def calc_average_salary_language_sj(lang=""):
    """Вычисление средней зарплаты по найденным вакансиям SuperJob из списка."""
    search_text = " ".join([SEARCH_TEXT_PART, lang])
    vacancies = fetch_all_vacancies_sj(search_text)
    average_salary = 0
    processed_vacancies = 0

    predicted_data = [
        predict_rub_salary_sj(vacancy)
        for vacancy in vacancies
    ]
    predicted_salaries = list(filter(None, predicted_data))
    predicted_salaries_number = len(predicted_salaries)
    try:
        average_salary = int(
            sum(predicted_salaries) / predicted_salaries_number
        )
    except ZeroDivisionError:
        average_salary = 0

    return  [
        lang,
        get_vacancies_found_number_sj(search_text),
        predicted_salaries_number,
        average_salary
    ]


def print_table(data, title=None):
    """Вывод таблицы результатов в консоль."""
    headers = [
        "Язык программирования", "Вакансий найдено",
        "Вакансий обработано", "Средняя зарплата"
    ]
    table_data = [headers]
    for item in data:
        table_data.append(
            list(map(str, item))
        )
    table = AsciiTable(table_data=table_data, title=title)
    print(table.table)


def main():
    try:
        avg_salaries_hh = calc_average_salary_all_languages(
            calc_func=calc_average_salary_language_hh
        )
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))

    try:
        avg_salaries_sj = calc_average_salary_all_languages(
            calc_func=calc_average_salary_language_sj
        )
    except HTTPError as error:
        exit("Невозможно получить данные с сервера:\n{0}\n".format(error))

    print_table(data=avg_salaries_hh, title="HeadHunter Moscow")
    print_table(data=avg_salaries_sj, title="SuperJob Moscow")


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
