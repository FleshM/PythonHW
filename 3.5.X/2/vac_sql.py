import sqlite3
import pandas as pd

con = sqlite3.connect('vacancies.db')
cur = con.execute('SELECT * FROM currencies')
currencies = list(map(lambda x: x[0], cur.description))[1:]
con.row_factory = sqlite3.Row
cur = con.cursor()

def format_salary(date, salary_from, salary_to, currency):
    """Считает среднюю зарплату вакансии в рублях, если известна хотя бы одна граница вилки оклада.

        Args:
            date(list[str]): Дата [год, месяц]
            salary_from(float): Нижняя граница вилки оклада
            salary_to(float): Верхняя граница вилки оклада
            currency(str): Валюта
        Returns:
            float: Средний оклад
    """
    exchange_rate = 1 if currency == 'RUR' else 0
    if currency in currencies:
        date = f"{date[1]}/{date[0]}"
        cur.execute("SELECT * FROM currencies WHERE date == :date", {"date": date})
        exchange_rate = cur.fetchall()[0][currency]
    if pd.notna(salary_from) and pd.notna(salary_to):
        return 0.5 * (salary_from + salary_to) * exchange_rate
    return salary_from * exchange_rate if pd.notna(salary_from) else salary_to * exchange_rate


df = pd.read_csv("vacancies_dif_currencies.csv")
salary = []
for index, row in df.iterrows():
    salary.append(format_salary(row["published_at"][0:7].split("-"), row["salary_from"],
                                row["salary_to"], row["salary_currency"]))

df.insert(1, 'salary', salary)
df = df.drop(columns=['salary_from', 'salary_to', 'salary_currency'])
df.to_sql("vacancies", con=con, index=False)
