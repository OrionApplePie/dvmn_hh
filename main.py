import requests
from requests.compat import urljoin


HH_API_BASE_URL = "https://api.hh.ru/"
VACANCIES_PATH = "/vacancies"
PROGRAMMING_LANGUAGES = (
    "JavaScript", "Java", "Python",
    "Ruby", "PHP", "C++",
    "C#", "Go", "Swift"
)

def fetch_vacancy_count_by_lang(lang=""):
    query_params = {
            "specialization": "1.221",
            "area": "1",
            "period": "30",
            "text": f"\"программист {lang}\""
        }
    fetch_url = urljoin(
        HH_API_BASE_URL, VACANCIES_PATH
    )
    response = requests.get(
        url=fetch_url,
        params=query_params 
    )
    response.raise_for_status()

    return response.json()["found"]


def main():
    langs_counts = {
        lang: fetch_vacancy_count_by_lang(lang=lang)
        for lang in PROGRAMMING_LANGUAGES
    }
    for lang in langs_counts:
        print(f"{lang}: {langs_counts[lang]}")


if __name__ == "__main__":
    main()
