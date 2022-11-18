import csv
import os
import openpyxl
from openpyxl.styles import Font, Border, Side
from openpyxl.styles.numbers import BUILTIN_FORMATS
import matplotlib.pyplot as plt
import numpy as np


class Vacancy:
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

    def __init__(self, vac, name):
        self.name = vac['name']
        self.salary_from = vac['salary_from']
        self.salary_to = vac['salary_to']
        self.salary_currency = vac['salary_currency']
        self.area_name = vac['area_name']
        self.published_at = vac['published_at']
        self.year = int(vac['published_at'].split('-')[0])
        self.salary = (float(self.salary_from) + float(self.salary_to)) / 2 * self.currency_to_rub[self.salary_currency]

        if self.year in DataSet.salary_by_year:
            DataSet.salary_by_year[self.year] += self.salary
        else:
            DataSet.salary_by_year[self.year] = self.salary

        if self.year in DataSet.vacancies_by_year:
            DataSet.vacancies_by_year[self.year] += 1
        else:
            DataSet.vacancies_by_year[self.year] = 1

        if name in self.name:
            if self.year in DataSet.p_name_salary_by_year:
                DataSet.p_name_salary_by_year[self.year] += self.salary
            else:
                DataSet.p_name_salary_by_year[self.year] = self.salary

            if self.year in DataSet.p_name_vacancies_by_year:
                DataSet.p_name_vacancies_by_year[self.year] += 1
            else:
                DataSet.p_name_vacancies_by_year[self.year] = 1

        if self.area_name in DataSet.salary_by_city:
            DataSet.salary_by_city[self.area_name] += self.salary
        else:
            DataSet.salary_by_city[self.area_name] = self.salary

        if self.area_name in DataSet.vacancies_by_city:
            DataSet.vacancies_by_city[self.area_name] += 1
        else:
            DataSet.vacancies_by_city[self.area_name] = 1


class DataSet:
    salary_by_year = {}
    vacancies_by_year = {}
    p_name_salary_by_year = {}
    p_name_vacancies_by_year = {}
    salary_by_city = {}
    vacancies_by_city = {}

    def __init__(self, file_name, p_name):
        self.file_name = file_name
        self.p_name = p_name

    def print_data(self):
        print(f'Динамика уровня зарплат по годам: {self.salary_by_year}')
        print(f'Динамика количества вакансий по годам: {self.vacancies_by_year}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {self.p_name_salary_by_year}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {self.p_name_vacancies_by_year}')
        print(f'Уровень зарплат по городам (в порядке убывания): {self.salary_by_city}')
        print(f'Доля вакансий по городам (в порядке убывания): {self.vacancies_by_city}')

    def get_data(self, data_vacancies):
        for vac in data_vacancies:
            Vacancy(vac, self.p_name)

        for year in self.vacancies_by_year:
            self.salary_by_year[year] = int(self.salary_by_year[year] / self.vacancies_by_year[year])

        length = len(self.p_name_salary_by_year)
        for year in self.p_name_salary_by_year:
            if length > 0:
                self.p_name_salary_by_year[year] = int(
                    self.p_name_salary_by_year[year] / self.p_name_vacancies_by_year[year])
            else:
                self.p_name_salary_by_year[year] = 0
                self.p_name_vacancies_by_year[year] = 0

        self.salary_by_city = {city: self.salary_by_city[city] / self.vacancies_by_city[city] for city in
                               self.salary_by_city}

        vac_amount = sum(self.vacancies_by_city.values())
        self.vacancies_by_city = {city: round(self.vacancies_by_city[city] / vac_amount, 4) for city in
                                  self.vacancies_by_city}

        self.salary_by_city = {city: int(self.salary_by_city[city]) for city in self.salary_by_city if
                               self.vacancies_by_city[city] > 0.01}
        self.vacancies_by_city = {city: self.vacancies_by_city[city] for city in self.vacancies_by_city if
                                  self.vacancies_by_city[city] > 0.01}

        self.salary_by_city = dict(sorted(self.salary_by_city.items(), key=lambda x: x[1], reverse=True))
        self.vacancies_by_city = dict(sorted(self.vacancies_by_city.items(), key=lambda x: x[1], reverse=True))

        self.salary_by_city = dict(list(self.salary_by_city.items())[:10])
        self.vacancies_by_city = dict(list(self.vacancies_by_city.items())[:10])

    def csv_filter(self, reader, list_naming):
        result = []
        for row in reader:
            is_correct = True
            if len(row) != len(list_naming):
                is_correct = False
            for v in row:
                if v == '':
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


class Report:
    def __init__(self):
        self.file = input('Введите название файла: ')
        self.name = input('Введите название профессии: ')

        self.data = DataSet(self.file, self.name)
        self.data.get_data(self.data.read_csv())

    def generate_image(self):
        labels = self.data.salary_by_year.keys()
        x = np.arange(len(labels))
        width = 0.35

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
        ax1.bar(x - width / 2, self.data.salary_by_year.values(), width, label='Средняя З/П')
        ax1.bar(x + width / 2, self.data.p_name_salary_by_year.values(), width, label=f'З/П {self.name}')

        ax1.set_title('Уровень зарплат по годам')
        ax1.set_xticks(x, labels, rotation=90, fontsize=8)
        ax1.legend(fontsize=8)
        ax1.grid(axis='y', linestyle='-')

        ax2.bar(x - width / 2, self.data.vacancies_by_year.values(), width, label='Количество вакансий')
        ax2.bar(x + width / 2, self.data.p_name_vacancies_by_year.values(), width,
                label=f'Количество вакансий\n{self.name}')

        ax2.set_title('Количество вакансий по годам')
        ax2.set_xticks(x, labels, rotation=90, fontsize=8)
        ax2.legend(fontsize=8)
        ax2.grid(axis='y', linestyle='-')

        self.data.salary_by_city = dict(sorted(self.data.salary_by_city.items(), key=lambda x: x[1]))
        cities = list(self.data.salary_by_city.keys())
        for i in range(len(cities)):
            cities[i] = cities[i].replace(' ', '\n')
            cities[i] = cities[i].replace('-', '-\n')

        x = np.arange(len(cities))

        ax3.barh(x, self.data.salary_by_city.values(), width * 2)

        ax3.set_title('Уровень зарплат по городам')
        ax3.set_yticks(x, cities, fontsize=6)
        ax3.grid(axis='x', linestyle='-')

        self.data.vacancies_by_city = dict(sorted(self.data.vacancies_by_city.items(), key=lambda x: x[1]))
        cities = list(self.data.vacancies_by_city.keys())
        cities.append('Другие')
        vacancies = list(self.data.vacancies_by_city.values())
        vacancies.append(1 - sum(vacancies))

        ax4.set_title('Доля вакансий по городам')
        ax4.pie(vacancies, labels=cities, textprops={'fontsize': 6})
        ax4.axis('equal')

        fig.tight_layout()

        plt.savefig('graph.png', dpi=300)

    def generate_excel(self):
        wb = openpyxl.Workbook()
        ws_years = wb.worksheets[0]
        ws_years.title = "Статистика по годам"
        ws_years.append(['Год', 'Средняя зарплата', f'Средняя зарплата - {self.name}',
                         'Количество вакансий', f'Количество вакансий - {self.name}'])

        for year in self.data.salary_by_year:
            ws_years.append([year, self.data.salary_by_year[year], self.data.p_name_salary_by_year[year],
                             self.data.vacancies_by_year[year], self.data.p_name_vacancies_by_year[year]])

        self.format_excel_data(ws_years)

        wb.create_sheet('Статистика по городам')
        ws_cities = wb.worksheets[1]
        ws_cities.append(['Город', 'Уровень зарплат', '', 'Город', 'Доля вакансий'])

        salary_list = list(self.data.salary_by_city.items())
        vacancy_list = list(self.data.vacancies_by_city.items())
        for i in range(len(salary_list)):
            ws_cities.append([salary_list[i][0], salary_list[i][1], '',
                              vacancy_list[i][0], vacancy_list[i][1]])

        self.format_excel_data(ws_cities)

        wb.save("report.xlsx")

    @staticmethod
    def format_excel_data(ws):
        thin = Side(border_style="thin", color="000000")
        dims = {}
        is_title = True
        for row in ws.rows:
            for cell in row:
                if cell.value == '':
                    dims[cell.column_letter] = 0
                    continue
                if type(cell.value) == float:
                    cell.number_format = BUILTIN_FORMATS[10]
                if cell.value:
                    if is_title:
                        cell.font = Font(bold=True)
                    cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
            is_title = False
        for col, value in dims.items():
            ws.column_dimensions[col].width = value + 2


report = Report()
report.data.print_data()
report.generate_image()
