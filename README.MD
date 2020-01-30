## Примечание

По непонятной причине на SuperJob находит мало вакансий по языкам программирования (По Мск).
М.б. их в принципе мало.


## TODO

- Сделать отдельные функции для получения количества всех вакансий по запросу.
  Эта инфа есть в возвращаемой структуре данных (ключ 'total' на SJ).

  Для hh.ru:

    ```
    def _get_vacancies_found_number_hh(search_text=""):
        """Get number of found response by search text."""
        response = _get_vacancies_page_hh(search_text=search_text,)
        response.raise_for_status()
        return response.json()["found"]
    ```

- Убрать магические числа в __fetch_all_vacancies_sj__

- Сделать __calc_average_salary_language_xx__ общей?

- Добавить "Программист" в поисковую фразу __search_text = lang__

- Выделить код с разной логикой hh/sj отдельно от доп. функций
