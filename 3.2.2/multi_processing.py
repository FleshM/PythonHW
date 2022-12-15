import cProfile
import multiprocessing
import csv
import os

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}


def csv_divider(file_name):
    """Разделяет csv-файл на отдельные файлы по годам.

        Args:
           file_name (str): Название csv-файла
    """
    with open(file_name, newline='', encoding='utf-8-sig') as file:
        header = file.readline()
        rows = []
        year = 0
        for row in file:
            current_year = int(row.split(',')[-1].split('-')[0])
            if year == 0:
                year = current_year
                rows.append(row)
            elif current_year == year:
                rows.append(row)
            else:
                with open('./csv/' + str(year) + '.csv', 'w', newline='', encoding='utf-8-sig') as out:
                    out.write(header)
                    out.writelines(rows)
                year = current_year
                rows = []
        if len(rows) > 0:
            with open('./csv/' + str(year) + '.csv', 'w', newline='', encoding='utf-8-sig') as out:
                out.write(header)
                out.writelines(rows)


def read_csv(file_name):
    """Читает csv файл и возвращает отформатированные данные.

    Returns:
        list[dict]: Список словарей
    """
    head, result = [], []
    with open(file_name, newline='', encoding='utf-8-sig') as File:
        reader = csv.reader(File)
        is_first = True
        for row in reader:
            if is_first:
                head = row
                is_first = False
                continue
            result.append(dict(zip(head, row)))
    return result


def get_year_statistics(file_name, p_name, queue):
    """Читает csv файл, формирует все (4) статистки за год и кладет их в очередь.

    Args:
        file_name(str): Название файла
        p_name(str): Название профессии
        queue(Queue): Очередь
    """
    year = int(file_name[4:8])
    salary_by_year = 0
    vacancies_by_year = 0
    p_name_salary_by_year = 0
    p_name_vacancies_by_year = 0
    data_vacancies = read_csv(file_name)

    for vac in data_vacancies:
        salary = (float(vac['salary_from']) + float(vac['salary_to'])) / 2 * currency_to_rub[vac['salary_currency']]
        salary_by_year += salary
        vacancies_by_year += 1
        if p_name in vac['name']:
            p_name_salary_by_year += salary
            p_name_vacancies_by_year += 1

    salary_by_year = int(salary_by_year / vacancies_by_year)
    p_name_salary_by_year = int(p_name_salary_by_year / p_name_vacancies_by_year)

    queue.put([year, salary_by_year, vacancies_by_year, p_name_salary_by_year, p_name_vacancies_by_year])


def get_multi_stats(p_name):
    """Создает отдельные процессы для каждого csv-файла и возвращает статистику по всем годам.

    Args:
        p_name(str): Название профессии

    Returns:
        list: Список, содержащий статистку по всем годам
    """
    queue = multiprocessing.Queue()
    processes = []
    for file_name in os.listdir("csv"):
        csv_file = os.path.join("csv", file_name)
        process = multiprocessing.Process(target=get_year_statistics, args=(csv_file, p_name, queue))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()

    result = [{} for i in range(4)]
    while not queue.empty():
        year_data = queue.get()
        for i in range(4):
            result[i][year_data[0]] = year_data[i + 1]

    for i in range(len(result)):
        result[i] = dict(sorted(result[i].items(), key=lambda x: x[0]))
    return result


def get_cities_stats(file_name):
    """Получает статистику по городам, не используя многопроцессорную обработку.

    Args:
        file_name(str): Название файла

    Returns:
        list: Список, содержащий статистку по городам
    """
    salary_by_city = {}
    vacancies_by_city = {}
    data_vacancies = read_csv(file_name)

    for vac in data_vacancies:
        current_city = vac['area_name']
        salary = (float(vac['salary_from']) + float(vac['salary_to'])) / 2 * currency_to_rub[vac['salary_currency']]

        if current_city in salary_by_city:
            salary_by_city[current_city] += salary
        else:
            salary_by_city[current_city] = salary

        if current_city in vacancies_by_city:
            vacancies_by_city[current_city] += 1
        else:
            vacancies_by_city[current_city] = 1

    salary_by_city = {city: salary_by_city[city] / vacancies_by_city[city] for city in
                      salary_by_city}

    vac_amount = sum(vacancies_by_city.values())
    vacancies_by_city = {city: round(vacancies_by_city[city] / vac_amount, 4) for city in
                         vacancies_by_city}

    salary_by_city = {city: int(salary_by_city[city]) for city in salary_by_city if
                      vacancies_by_city[city] > 0.01}
    vacancies_by_city = {city: vacancies_by_city[city] for city in vacancies_by_city if
                         vacancies_by_city[city] > 0.01}

    salary_by_city = dict(sorted(salary_by_city.items(), key=lambda x: x[1], reverse=True))
    vacancies_by_city = dict(sorted(vacancies_by_city.items(), key=lambda x: x[1], reverse=True))

    salary_by_city = dict(list(salary_by_city.items())[:10])
    vacancies_by_city = dict(list(vacancies_by_city.items())[:10])

    return [salary_by_city, vacancies_by_city]


if __name__ == "__main__":
    file = input('Введите название файла: ')
    name = input('Введите название профессии: ')
    csv_divider(file)
    year_stats = get_multi_stats(name)
    cities_stats = get_cities_stats(file)
    print(f"Динамика уровня зарплат по годам: {year_stats[0]}")
    print(f"Динамика количества вакансий по годам: {year_stats[1]}")
    print(f"Динамика уровня зарплат по годам для выбранной профессии: {year_stats[2]}")
    print(f"Динамика количества вакансий по годам для выбранной профессии: {year_stats[3]}")
    print(f"Уровень зарплат по городам (в порядке убывания): {cities_stats[0]}")
    print(f"Доля вакансий по городам (в порядке убывания): {cities_stats[1]}")
