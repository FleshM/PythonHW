import csv
import os
from datetime import datetime
import prettytable
import re


def remove_html(string):
    result = re.sub(r'<.*?>', '', string)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


def shortener(val):
    return val if len(val) <= 100 else val[:100] + '...'


class Salary:
    currencies = {
        'AZN': 'Манаты',
        'BYR': 'Белорусские рубли',
        'EUR': 'Евро',
        'GEL': 'Грузинский лари',
        'KGS': 'Киргизский сом',
        'KZT': 'Тенге',
        'RUR': 'Рубли',
        'UAH': 'Гривны',
        'USD': 'Доллары',
        'UZS': 'Узбекский сум'
    }

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

    salary_gross_dict = {
        'True': 'Без вычета налогов',
        'False': 'С вычетом налогов',
    }

    def __init__(self, vac):
        self.salary_from = int(float(vac['salary_from']))
        self.salary_to = int(float(vac['salary_to']))
        self.salary_gross = vac['salary_gross']
        self.salary_currency = vac['salary_currency']
        self.salary = self.get_salary()

    def get_average(self):
        return (float(self.salary_from) + float(self.salary_to)) / 2 * self.currency_to_rub[self.salary_currency]

    def get_salary(self):
        return '{0:,} - {1:,} ({2}) ({3})'.format(self.salary_from, self.salary_to,
                                                  Salary.currencies[self.salary_currency],
                                                  self.salary_gross_dict[self.salary_gross]).replace(',', ' ')


class Vacancy:
    bools = {
        'True': 'Да',
        'False': 'Нет',
        'TRUE': 'Да',
        'FALSE': 'Нет'
    }
    job_exp = {
        'noExperience': 'Нет опыта',
        'between1And3': 'От 1 года до 3 лет',
        'between3And6': 'От 3 до 6 лет',
        'moreThan6': 'Более 6 лет'
    }

    def __init__(self, vac):
        self.name = remove_html(vac['name'])
        self.description = shortener(remove_html(vac['description']))
        self.skills = vac['key_skills'].split('\n')
        self.key_skills = shortener(vac['key_skills'].replace('\r', ''))
        self.experience_id = self.job_exp[vac['experience_id']]
        self.premium = self.bools[vac['premium']]
        self.employer_name = vac['employer_name']
        self.salary = Salary(vac)
        self.area_name = vac['area_name']
        self.date = '{0[2]}.{0[1]}.{0[0]}'.format(vac['published_at'][:10].split('-'))
        self.published_at = vac['published_at']


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = []

    def get_data(self, data_vacancies):
        for vac in data_vacancies:
            self.vacancies_objects.append(Vacancy(vac))

    def csv_filter(self, reader, list_naming):
        result = []
        for row in reader:
            is_correct = True
            if len(row) != len(list_naming):
                is_correct = False
            for i in range(len(row)):
                if row[i] == '':
                    is_correct = False
            if is_correct:
                result.append(dict(zip(list_naming, row)))
        return result

    def read_csv(self):
        head, result = [], []
        if os.stat(self.file_name).st_size == 0:
            print('Пустой файл')
            exit()
        with open(self.file_name, newline='', encoding='utf-8-sig') as File:
            reader = csv.reader(File)
            is_first = True
            for row in reader:
                if is_first:
                    head = row
                    is_first = False
                    continue
                result.append(row)
        if len(result) == 0:
            print('Нет данных')
            exit()
        return self.csv_filter(result, head)


class InputConnect:
    header = ['Навыки', 'Оклад', 'Дата публикации вакансии', 'Опыт работы', 'Премиум-вакансия',
              'Идентификатор валюты оклада', 'Название', 'Название региона', 'Компания']

    keys_dict = ['name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name', 'area_name',
                 'published_at']

    experience_weight = {
        'Нет опыта': 0,
        'От 1 года до 3 лет': 1,
        'От 3 до 6 лет': 2,
        'Более 6 лет': 3
    }

    rus_dict = {
        '№': '№',
        'name': 'Название',
        'description': 'Описание',
        'key_skills': 'Навыки',
        'experience_id': 'Опыт работы',
        'premium': 'Премиум-вакансия',
        'employer_name': 'Компания',
        'salary_from': 'Оклад',
        'area_name': 'Название региона',
        'published_at': 'Дата публикации вакансии',
    }
    eng_dict = {
        '№': '№',
        'Название': 'name',
        'Описание': 'description',
        'Навыки': 'key_skills',
        'Опыт работы': 'experience_id',
        'Премиум-вакансия': 'premium',
        'Компания': 'employer_name',
        'Оклад': 'salary_from',
        'Название региона': 'area_name',
        'Дата публикации вакансии': 'published_at'
    }

    filters_dict = {
        'Название': lambda vac, value: vac.name == value,
        'Навыки': lambda vac, value: all([s in vac.skills for s in value.split(', ')]),
        'Опыт работы': lambda vac, value: vac.experience_id == value,
        'Премиум-вакансия': lambda vac, value: vac.premium == value,
        'Компания': lambda vac, value: vac.employer_name == value,
        'Оклад': lambda vac, value: vac.salary.salary_from <= float(value) <= vac.salary.salary_to,
        'Идентификатор валюты оклада': lambda vac, value: Salary.currencies[vac.salary.salary_currency] == value,
        'Название региона': lambda vac, value: vac.area_name == value,
        'Дата публикации вакансии': lambda vac, value: vac.date == value,
    }

    def __init__(self):
        self.file = input('Введите название файла: ')
        self._filter = input('Введите параметр фильтрации: ')
        self._sort = input('Введите параметр сортировки: ')
        self.is_reverse = input('Обратный порядок сортировки (Да / Нет): ')
        self.segment = input('Введите диапазон вывода: ')
        self.fields = input('Введите требуемые столбцы: ')

        self.validate()

        data = DataSet(self.file)
        data.get_data(data.read_csv())
        self.print_table(data.vacancies_objects, self.rus_dict, self.keys_dict)

    def validate(self):
        self.validate_segment()
        self.validate_filter()
        self.validate_sort()
        self.validate_reverse()

    def validate_segment(self):
        result = []
        if len(self.segment) > 0:
            result = [int(i) for i in self.segment.split(' ')]
        self.segment = result

    def validate_filter(self):
        if len(self._filter) == 0:
            self._filter = True
            return
        if len(self._filter) > 0 and ': ' not in self._filter:
            print('Формат ввода некорректен')
            exit()
        result = self._filter.split(': ')
        if result[0] not in self.header:
            print('Параметр поиска некорректен')
            exit()
        self._filter = result

    def validate_sort(self):
        if len(self._sort) == 0:
            self._sort = True
            return
        if self._sort not in self.header:
            print('Параметр сортировки некорректен')
            exit()

    def validate_reverse(self):
        if len(self.is_reverse) == 0:
            self.is_reverse = False
            return
        if self.is_reverse == 'Да':
            self.is_reverse = True
            return
        if self.is_reverse == 'Нет':
            self.is_reverse = False
            return
        else:
            print('Порядок сортировки задан некорректно')
            exit()

    def print_table(self, data_vacancies, dic_naming, keys):
        table = prettytable.PrettyTable()
        table.hrules = prettytable.ALL
        table.align = 'l'
        table.field_names = dic_naming.values()
        table.max_width = 20
        self.do_sort(data_vacancies)
        data_vacancies = self.filter_vacs(data_vacancies)
        result = self.get_result(data_vacancies)
        if len(result) == 0:
            print('Ничего не найдено')
            return
        else:
            table.add_rows(result)
        if len(self.fields) == 0:
            self.fields = dic_naming.values()
        else:
            self.fields = ('№, ' + self.fields).split(', ')
        print(table.get_string(fields=self.fields))

    def get_result(self, data_vacancies):
        result = []
        length = len(self.segment)
        i = 0
        for vac in data_vacancies:
            i += 1
            if (length > 1 and self.segment[0] <= i < self.segment[1]) or (
                    length == 1 and self.segment[0] <= i) or length == 0:
                result.append([i, vac.name, vac.description, vac.key_skills, vac.experience_id, vac.premium,
                               vac.employer_name, vac.salary.salary, vac.area_name, vac.date])
        return result

    def filter_vacs(self, data_vacancies):
        if self._filter == True:
            return data_vacancies
        return list(
            filter(lambda vac: self.filters_dict[self._filter[0]](vac, self._filter[1]), data_vacancies))

    def do_sort(self, data_vacancies):
        if self._sort == True:
            return
        if self._sort == 'Дата публикации вакансии':
            data_vacancies.sort(reverse=self.is_reverse,
                                key=lambda v: datetime.strptime(v.published_at, '%Y-%m-%dT%H:%M:%S%z'))
            return
        if self._sort == 'Навыки':
            data_vacancies.sort(reverse=self.is_reverse,
                                key=lambda v: len(v.skills) if type(v.skills) == list else 1)
            return
        if self._sort == 'Оклад':
            data_vacancies.sort(reverse=self.is_reverse, key=lambda v: v.salary.get_average())
            return
        if self._sort == 'Опыт работы':
            data_vacancies.sort(reverse=self.is_reverse,
                                key=lambda v: self.experience_weight[v.experience_id])
            return
        data_vacancies.sort(reverse=self.is_reverse, key=lambda v: getattr(v, self.eng_dict[self._sort]))
