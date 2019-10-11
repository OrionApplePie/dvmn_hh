from itertools import count

import requests
from requests.compat import urljoin


HH_API_BASE_URL = "https://api.hh.ru/"
VACANCIES_PATH = "/vacancies"

PROGRAMMER_SPEC_ID = "1.221"
AREA_MOSCOW = "1"
VACANCY_PERIOD = "30"

PROGRAMMING_LANGUAGES = (
    "JavaScript", "Java", "Python"
    # "Ruby", "PHP", "C++",
    # "C#", "Go", "Swift"
)


def get_vacancies(search_text="", page=0):
    """Request to /vacancies API endpoint."""

    query_params = {
        "specialization": PROGRAMMER_SPEC_ID,
        "area":   AREA_MOSCOW,
        "period": VACANCY_PERIOD,

        "text": search_text,
        "page": page
    }

    url = urljoin(
        HH_API_BASE_URL, VACANCIES_PATH
    )

    response = requests.get(
        url=url,
        params=query_params 
    )
    response.raise_for_status()

    return response


def predict_rub_salary(vacancy=None):
    """Calculate average salary of given vacancy
    or return None if no information of salary.
    Process only if currency is RUR."""

    salary = vacancy["salary"]

    if salary is None:
        return None

    if salary["currency"] != "RUR":
        return None

    salary_from = salary["from"]
    salary_to = salary["to"]
    average_salary = 0

    if salary_from is not None and salary_to is not None:
        average_salary = (salary_from + salary_to) / 2

    if salary_from is not None and salary_to is None:
        average_salary = salary_from * 1.2 

    if salary_from is None and salary_to is not None:
        average_salary = salary_to * 0.8 

    return int(average_salary)


def get_vacancies_found_number(search_text=""):
    """Get number of found vacancies by search text."""
    response = get_vacancies(
        search_text=search_text,
    )
    return int(
        response.json()["found"]
    )


def fetch_all_vacancies(search_text="", start_page=0):
    """Fetch all vacancies from every pages. (API limit is 2000)."""
    for page in count(start_page):
        print(f"fetch by search text: {search_text}, page: {page}")
        response = get_vacancies(
            search_text=search_text,
            page=page
        )
        page_data = response.json()

        if page >= page_data["pages"] - 1:
            break

        yield from page_data["items"]


def calc_average_salary_language(lang=""):
    """Caclculate average salary of vacancies by given language."""

    search_text = lang
    print(f"fetch {lang} vacancies...")  # fix me!!!
    vacancies_found = get_vacancies_found_number(
        search_text=search_text
    )
    all_vacancies = fetch_all_vacancies(
        search_text=search_text,
    )

    vacancies_with_salary = [
        predict_rub_salary(vacancy)
        for vacancy in all_vacancies
        if predict_rub_salary(vacancy) is not None
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


def main():
    
    avg_salaries = []

    for lang in PROGRAMMING_LANGUAGES:
        avg_salaries.append(
            calc_average_salary_language(lang=lang)
        )

    for lang_salary in avg_salaries:
        for name in lang_salary.keys():
            info = lang_salary[name]
            print(
                (f'{name} / found: {info["vacancies_found"]} /'
                 f' processed: {info["vacancies_processed"]} /'
                 f' avg salary: {info["average_salary"]} ')
            )

if __name__ == "__main__":
    main()
 