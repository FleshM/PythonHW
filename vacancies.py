import csv
import os
from datetime import datetime
import prettytable
import re
import doctest


def remove_html(string):
    """Очищает строку от html тегов.

    Args:
        string (str): Исходная строка

    Returns:
        str: Строка без html тегов

    >>> remove_html("<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>Работать в составе команды")
    'Вам предстоит: Работать в составе команды'
    >>> remove_html("<p>")
    ''
    """
    result = re.sub(r'<.*?>', '', string)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


def shortener(string):
    """Обрезает исходную строку до 100 символов.

    Args:
        string (str): Исходная строка

    Returns:
        str: Строка (до 100 символов)

    >>> shortener("«Самокат» — это технологическая компания и один из самых быстро растущих проектов в России. Мы меняе")
    '«Самокат» — это технологическая компания и один из самых быстро растущих проектов в России. Мы меняе'
    >>> shortener("«Самокат» — это технологическая компания и один из самых быстро растущих проектов в России. Мы меняем")
    '«Самокат» — это технологическая компания и один из самых быстро растущих проектов в России. Мы меняе...'
    """
    return string if len(string) <= 100 else string[:100] + '...'


class Salary:
    """Класс для представления зарплаты.

    Attributes:
        salary_from (int): Нижняя граница вилки оклада
        salary_to (int): Верхняя граница вилки оклада
        salary_gross (str): Вычет налогов
        salary_currency (str): Валюта
        salary (str): Оклад
        currencies (dict[str, str]): Словарь с валютами
        currency_to_rub (dict[str, float]): Словарь с валютами для превода зарплаты в рубли
        salary_gross_dict (dict[str, str]): Словарь типов вычета налогов для перевода с английского на русский
    """
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
        """Инициализирует объект Salary, выполянет конвертацию для целочисленных полей, форматирует оклад.

        Args:
            vac (dict): Вакансия в виде словаря

        >>> Salary({'salary_from': '1', 'salary_to': '10', 'salary_gross': True, 'salary_currency': "RUR"})
        Traceback (most recent call last):
            ...
        KeyError: True
        >>> Salary({'salary_from': 'ABC', 'salary_to': '10', 'salary_gross': 'True', 'salary_currency': "BYR"})
        Traceback (most recent call last):
            ...
        ValueError: could not convert string to float: 'ABC'
        >>> Salary({'salary_from': '1', 'salary_to': 10, 'salary_gross': 'True', 'salary_currency': 1})
        Traceback (most recent call last):
            ...
        KeyError: 1
        """
        self.salary_from = int(float(vac['salary_from']))
        self.salary_to = int(float(vac['salary_to']))
        self.salary_gross = vac['salary_gross']
        self.salary_currency = vac['salary_currency']
        self.salary = self.get_salary()

    def get_average(self):
        """Вычисляет среднюю зарплату и переводит ее в рубли, с помощью словаря currency_to_rub.

        Returns:
            float: Средняя зарплата в рублях
        >>> Salary({'salary_from': '1', 'salary_to': 10, 'salary_gross': 'True', 'salary_currency': "BYR"}).get_average()
        131.505
        >>> Salary({'salary_from': 200, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR"}).get_average()
        200.0
        >>> Salary({'salary_from': '200', 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "рубли"}).get_average()
        Traceback (most recent call last):
            ...
        KeyError: 'рубли'
        """
        return (float(self.salary_from) + float(self.salary_to)) / 2 * self.currency_to_rub[self.salary_currency]

    def get_salary(self):
        """Возвращает отформатированную строку оклада, используя зарплатную вилку, валюту и gross.

        Returns:
            str: Оклад

        >>> Salary({'salary_from': '1', 'salary_to': 10, 'salary_gross': 'False', 'salary_currency': "BYR"}).get_salary()
        '1 - 10 (Белорусские рубли) (С вычетом налогов)'
        >>> Salary({'salary_from': 200, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR"}).get_salary()
        '200 - 200 (Рубли) (Без вычета налогов)'
        >>> Salary({'salary_from': '200', 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "рубли"}).get_salary()
        Traceback (most recent call last):
            ...
        KeyError: 'рубли'
        """
        return '{0:,} - {1:,} ({2}) ({3})'.format(self.salary_from, self.salary_to,
                                                  Salary.currencies[self.salary_currency],
                                                  self.salary_gross_dict[self.salary_gross]).replace(',', ' ')


class Vacancy:
    """Класс для представления вакансии.

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии (до 100 символов)
        skills (list[str]): Список всех навыков
        key_skills (str): Навыки (до 100 символов)
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Название компании
        salary (Salary): Зарплата
        area_name (str): Город
        date (str): Отформатированная дата публикации
        published_at (str): Дата и время публикации
        bools (dict[str, str]): Словарь булевых перменных для перевода с английского на русский
        job_exp (dict[str, str]): Словарь типов опыта работы для перевода с английского на русский
    """
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
        """Инициализирует объект Vacancy и валидирует данные.

        Args:
            vac (dict): Вакансия в виде словаря

        >>> Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).skills
        ['Программирование']
        >>> Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).key_skills
        'Программирование'
        >>> Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).experience_id
        'Нет опыта'
        >>> Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).premium
        'Да'
        >>> type(Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).salary).__name__
        'Salary'
        >>> Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}).date
        '21.06.2022'
        >>> Vacancy({'salary_from': '1', 'salary_to': '10', 'salary_gross': True, 'salary_currency': "RUR"})
        Traceback (most recent call last):
            ...
        KeyError: 'name'
        """
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
    """Класс для представления датасета.

    Attributes:
        file_name (str): Название файла
        vacancies_objects (list[Vacancy]): Cписок всех вакансий
    """
    def __init__(self, file_name):
        """Инициализирует объект DataSet.

        Args:
            file_name (str): Название файла, откуда нужно получить данные
        """
        self.file_name = file_name
        self.vacancies_objects = []

    def get_data(self, data_vacancies):
        """Заполняет список всех вакансий (vacancies_objects) объектами Vacancy.

        Args:
            data_vacancies (list[dict]): Список со всеми вакансиями в виде словарей
        >>> data = DataSet('file')
        >>> data.get_data([{'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}])
        >>> type(data.vacancies_objects[0]).__name__
        'Vacancy'
        >>> data.vacancies_objects[0].name
        'Программист'
        """
        for vac in data_vacancies:
            self.vacancies_objects.append(Vacancy(vac))

    def csv_filter(self, reader, list_naming):
        """Форматирует данные полученные после чтения csv файла и возвращает результат.

        Args:
            reader (list): Данные полученные после чтения csv файла
            list_naming (list[str]): Список с ключами для создания словаря

        Returns:
            list[dict]: Список словарей
        """
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
        """Читает csv файл и возвращает отформатированные данные.

        Returns:
            list[dict]: Список словарей

        >>> DataSet('test1.csv').read_csv()
        [{'name': 'Web-программист', 'description': '<p>NEW! Web-программист(без опыта и с опытом)</p> <p> </p> <p><strong>Обязанности</strong>:</p> <p>- верстка сайтов на основе готовых макетов PHP, HTML и CSS</p> <p>- подключение собственной системы управления(обучение)</p> <p>- развитие собственного движка и системы управления</p> <p>- установка движка организации на проектах (обучение)</p> <p><br /><strong>Требования:</strong></p> <ul> <li>PHP7.4+ (знания ООП и паттернов проектирования) MySQL(MariaDB,PostgresQL)</li> <li>CSS(LESS,SASS)</li> <li>JS(TypeScript,NodeJS)</li> <li>знание основ Figma / Photoshop(для верстки с макетов из PSD)</li> <li>остальное при собеседовании.</li> </ul> <p><br /><strong>Условия:</strong></p> <p>- работа с офисе на Московское шоссе (удаленка после испытательного срока)</p> <p>- 5 дней с 9-00 до 18-00 (после вхождения в работу график может быть плавающим)</p> <p>- чай кофе печеньки</p> <p>- дружный коллектив</p> <p>- отпуск ежегодный оплачиваемый</p> <p> </p> <p><strong>В целом рассматриваем как с опытом работы так и без опыта. Если человек готов учиться и развиваться, он предан и любит программировать и верстать сайты мы его научим и подготовим за счет компании.</strong></p> <p> </p> <p>Испытательный срок от 2 до 4 недель(при собеседовании)</p> <p>Зарплата 2 раза в месяц: аванс и оклад.</p> <p><strong>Оклад фиксированный</strong> + <strong>% от объема</strong> выполненных задач за месяц.</p>', 'key_skills': 'Разработка ПО', 'experience_id': 'noExperience', 'premium': 'False', 'employer_name': 'Асташенков Г. А.', 'salary_from': '30000.0', 'salary_to': '80000.0', 'salary_gross': 'False', 'salary_currency': 'RUR', 'area_name': 'Ульяновск', 'published_at': '2022-05-31T17:32:31+0300'}]
        >>> DataSet('test99.csv').read_csv()
        Traceback (most recent call last):
            ...
        FileNotFoundError: [WinError 2] Не удается найти указанный файл: 'test99.csv'
        >>> DataSet('test2.csv').read_csv()
        []
        """
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
    """Класс для валидации введенных данных и запуска программы.

    Attributes:
        file (str): Название файла
        _filter (bool or list[str]): Параметр фильтрации (True, если параметр не введен)
        _sort (bool or str): Параметр сортировки (True, если параметр не введен)
        is_reverse (bool): Обратный порядок сортировки
        segment (list[int]): Диапазон вывода
        fields (list[str] or str): Требуемые столбцы
        header (list[str]): Список заголовков
        keys_dict (list[str]): Список ключей в словаре
        experience_weight (dict[str, int]): Вес в зависимости от опыта работы
        rus_dict (dict[str, str]): Словарь для перевода ключей с английского на русский
        eng_dict (dict[str, str]): Словарь для перевода ключей с русского на английский
        filters_dict (dict[str, () -> bool]): Словарь фильтров
    """
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
        """Инициализирует объект InputConnect, валидирует введенные данные и запускает программу.

        """
        self.file = input('Введите название файла: ')
        self._filter = input('Введите параметр фильтрации: ')
        self._sort = input('Введите параметр сортировки: ')
        self.is_reverse = input('Обратный порядок сортировки (Да / Нет): ')
        self.segment = input('Введите диапазон вывода: ')
        self.fields = input('Введите требуемые столбцы: ')

        self.validate()

        data = DataSet(self.file)
        data.get_data(data.read_csv())
        self.print_table(data.vacancies_objects, self.rus_dict)

    def validate(self):
        """Запускает функции валидации для каждой перменной.

        """
        self.validate_segment()
        self.validate_filter()
        self.validate_sort()
        self.validate_reverse()

    def validate_segment(self):
        """Валидирует введенный диапазон, преобразуя его из строки в список list[int].

        """
        result = []
        if len(self.segment) > 0:
            result = [int(i) for i in self.segment.split(' ')]
        self.segment = result

    def validate_filter(self):
        """Валидирует введенный параметр фильрации, преобразуя его из строки в список list[str].
        Если параметр не был введен, то _filter = True.

        """
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
        """Валидирует введенный параметр сортировки. Если параметр не был введен, то _sort = True.

        """
        if len(self._sort) == 0:
            self._sort = True
            return
        if self._sort not in self.header:
            print('Параметр сортировки некорректен')
            exit()

    def validate_reverse(self):
        """Валидирует введенный параметр обратной сортировки. Преобразует строку в булеан, по умолчанию - False.

        """
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

    def print_table(self, data_vacancies, dic_naming):
        """Метод для печати таблицы. Перед печатью, данные сортируются и фильтруются. Далее выводится таблица
        с необходимым диапазоном и выбранными столбцами.

        Args:
            data_vacancies (list[Vacancy]): Cписок всех вакансий
            dic_naming (dict[str, str]): Словарь с заголовками столбцов
        """
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
            self.fields = ('№, ' + str(self.fields)).split(', ')
        print(table.get_string(fields=self.fields))

    def get_result(self, data_vacancies):
        """Метод для получения всех необходимых рядов таблицы, учитывая диапазон.

        Args:
            data_vacancies (list[Vacancy]): Cписок всех вакансий

        Returns:
            list[list[int | str]]: Список всех необходимых рядов таблицы
        """
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
        """Метод для фильтрации вакансий. Использует словарь - filters_dict.
        Если параметр фильтрации не задан, возвращает исходный список.

        Args:
            data_vacancies (list[Vacancy]): Cписок всех вакансий

        Returns:
            list[Vacancy]: Список отфильтрованных вакансий
        """
        if self._filter == True:
            return data_vacancies
        return list(
            filter(lambda vac: self.filters_dict[self._filter[0]](vac, self._filter[1]), data_vacancies))

    def do_sort(self, data_vacancies):
        """Метод для сортировки вакансий. Если параметр сортировки не задан, список остается без изменений.

        Args:
            data_vacancies (list[]): Cписок всех вакансий
        """
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
