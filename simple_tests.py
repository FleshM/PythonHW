import unittest

import statistics
from vacancies import InputConnect, Vacancy


class InputConnectTests(unittest.TestCase):
    def test_type(self):
        self.assertEqual(type(InputConnect()).__name__, 'InputConnect')

    def test_result(self):
        vac = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        self.assertEqual(InputConnect().get_result([vac]), [[1, 'Программист', 'Вам предстоит: :', 'Программирование', 'Нет опыта', 'Да', 'URFU', '100 - 200 (Рубли) (Без вычета налогов)', 'Ekat', '21.06.2022']])

    def test_sort_date(self):
        # Введите параметр сортировки: Дата публикации вакансии
        vac1 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2023-06-21T17:33:46+0300"})
        vac2 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        vac_list = [vac1, vac2]
        InputConnect().do_sort(vac_list)
        self.assertEqual(vac_list[0].date, '21.06.2022')

    def test_sort_exp(self):
        # Введите параметр сортировки: Опыт работы
        vac1 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2023-06-21T17:33:46+0300"})
        vac2 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'between3And6', 'premium': 'True', 'employer_name': "URFU", 'salary_from': 100, 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        vac_list = [vac1, vac2]
        InputConnect().do_sort(vac_list)
        self.assertEqual(vac_list[1].experience_id, 'От 3 до 6 лет')

    def test_sort_salary(self):
        # Введите параметр сортировки: Оклад
        vac1 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100000', 'salary_to': '150000', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2023-06-21T17:33:46+0300"})
        vac2 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'between3And6', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100', 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        vac_list = [vac1, vac2]
        InputConnect().do_sort(vac_list)
        self.assertEqual(vac_list[1].salary.salary, '100 000 - 150 000 (Рубли) (Без вычета налогов)')

    def test_reverse_sort(self):
        # Введите параметр сортировки: Оклад
        # Обратный порядок сортировки (Да / Нет): Да
        vac1 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100000', 'salary_to': '150000', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2023-06-21T17:33:46+0300"})
        vac2 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'between3And6', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100', 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        vac_list = [vac1, vac2]
        InputConnect().do_sort(vac_list)
        self.assertEqual(vac_list[0].salary.salary, '100 000 - 150 000 (Рубли) (Без вычета налогов)')

    def test_filter(self):
        # Введите параметр фильтрации: Название: Программист
        vac1 = Vacancy({'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100000', 'salary_to': '150000', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2023-06-21T17:33:46+0300"})
        vac2 = Vacancy({'name': 'Аналитик', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:', 'key_skills': "Программирование", 'experience_id': 'between3And6', 'premium': 'True', 'employer_name': "URFU", 'salary_from': '100', 'salary_to': '200', 'salary_gross': 'True', 'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"})
        vac_list = [vac1, vac2]
        self.assertEqual(InputConnect().filter_vacs(vac_list)[0].name, 'Программист')


class VacancyTest(unittest.TestCase):
    def test_init(self):
        dict = {'name': 'Программист', 'description': '<p> </p> <p><strong>Вам предстоит:</strong></p> <ul> <li>:',
                'key_skills': "Программирование", 'experience_id': 'noExperience', 'premium': 'True',
                'employer_name': "URFU", 'salary_from': '100000', 'salary_to': '150000', 'salary_gross': 'True',
                'salary_currency': "RUR", 'area_name': 'Ekat', 'published_at': "2022-06-21T17:33:46+0300"}
        name = 'Программист'
        vac = statistics.Vacancy(dict, name)

        self.assertEqual(vac.name, 'Программист')
        self.assertEqual(vac.year, 2022)
        self.assertEqual(vac.salary, 125000.0)

        self.assertEqual(statistics.DataSet.salary_by_year[vac.year], 125000.0)
        self.assertEqual(statistics.DataSet.p_name_salary_by_year[vac.year], 125000.0)
        self.assertEqual(statistics.DataSet.vacancies_by_year[vac.year], 1)
        self.assertEqual(statistics.DataSet.p_name_vacancies_by_year[vac.year], 1)
        self.assertEqual(statistics.DataSet.vacancies_by_city['Ekat'], 1)
        self.assertEqual(statistics.DataSet.salary_by_city['Ekat'], 125000.0)


class DataSetTests(unittest.TestCase):
    def test_csv(self):
        dataset = statistics.DataSet('test1.csv', 'Программист')
        self.assertEqual(dataset.read_csv(), [{'name': 'Web-программист', 'description': '<p>NEW! Web-программист(без опыта и с опытом)</p> <p> </p> <p><strong>Обязанности</strong>:</p> <p>- верстка сайтов на основе готовых макетов PHP, HTML и CSS</p> <p>- подключение собственной системы управления(обучение)</p> <p>- развитие собственного движка и системы управления</p> <p>- установка движка организации на проектах (обучение)</p> <p><br /><strong>Требования:</strong></p> <ul> <li>PHP7.4+ (знания ООП и паттернов проектирования) MySQL(MariaDB,PostgresQL)</li> <li>CSS(LESS,SASS)</li> <li>JS(TypeScript,NodeJS)</li> <li>знание основ Figma / Photoshop(для верстки с макетов из PSD)</li> <li>остальное при собеседовании.</li> </ul> <p><br /><strong>Условия:</strong></p> <p>- работа с офисе на Московское шоссе (удаленка после испытательного срока)</p> <p>- 5 дней с 9-00 до 18-00 (после вхождения в работу график может быть плавающим)</p> <p>- чай кофе печеньки</p> <p>- дружный коллектив</p> <p>- отпуск ежегодный оплачиваемый</p> <p> </p> <p><strong>В целом рассматриваем как с опытом работы так и без опыта. Если человек готов учиться и развиваться, он предан и любит программировать и верстать сайты мы его научим и подготовим за счет компании.</strong></p> <p> </p> <p>Испытательный срок от 2 до 4 недель(при собеседовании)</p> <p>Зарплата 2 раза в месяц: аванс и оклад.</p> <p><strong>Оклад фиксированный</strong> + <strong>% от объема</strong> выполненных задач за месяц.</p>', 'key_skills': 'Разработка ПО', 'experience_id': 'noExperience', 'premium': 'False', 'employer_name': 'Асташенков Г. А.', 'salary_from': '30000.0', 'salary_to': '80000.0', 'salary_gross': 'False', 'salary_currency': 'RUR', 'area_name': 'Ульяновск', 'published_at': '2022-05-31T17:32:31+0300'}])

    def test_result(self):
        dataset = statistics.DataSet('test3.csv', 'Аналитик')
        dataset.get_data(dataset.read_csv())

        self.assertEqual(dataset.salary_by_year, {2007: 55625.0})
        self.assertEqual(dataset.p_name_salary_by_year, {2007: 57500.0})
        self.assertEqual(dataset.vacancies_by_year, {2007: 4})
        self.assertEqual(dataset.p_name_salary_by_year, {2007: 57500.0})
        self.assertEqual(dataset.salary_by_city, {'Москва': 62500, 'Санкт-Петербург': 48750})
        self.assertEqual(dataset.vacancies_by_city, {'Москва': 0.5, 'Санкт-Петербург': 0.5})




