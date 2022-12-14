import pandas as pd

df = pd.read_csv("vacancies_dif_currencies.csv")
currency_dates = pd.read_csv("currencies.csv")
currencies = list(currency_dates.columns)[1:len(list(currency_dates.columns))]

def format_salary(date, salary_from, salary_to, currency):
    exchange_rate = 1 if currency == 'RUR' else 0
    if currency in currencies:
        date = f"{date[1]}/{date[0]}"
        exchange_rate = currency_dates.loc[currency_dates["date"] == date][currency].values[0]

    if pd.notna(salary_from) and pd.notna(salary_to):
        return 0.5 * (salary_from + salary_to) * exchange_rate
    elif pd.notna(salary_from):
        return salary_from * exchange_rate
    else:
        return salary_to * exchange_rate

salary = []
for index, row in df.iterrows():
    salary.append(format_salary(row["published_at"][0:7].split("-"), row["salary_from"], row["salary_to"], row["salary_currency"]))

df.insert(1, 'salary', salary)
df = df.drop(columns = ['salary_from', 'salary_to', 'salary_currency'])
df[0:100].to_csv("vacancies.csv", index=False)
