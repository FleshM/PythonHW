import pandas as pd
import requests

df = pd.read_csv("vacancies_dif_currencies.csv")
published_at_df = df["published_at"]
first_date = published_at_df.min()[0:7].split('-')
last_date = published_at_df.max()[0:7].split('-')

currencies = df.groupby("salary_currency").size()
currencies = {cur: 0 for cur in currencies.index if currencies[cur] > 5000 and cur != 'RUR'}
result = pd.DataFrame(columns=["date"] + list(currencies.keys()))

cur_codes = list(currencies.keys())
if 'BYR' in cur_codes:
    cur_codes.append('BYN')

dates = []
for year in range(int(first_date[0]), int(last_date[0]) + 1):
    for month in range(int(first_date[1]) if year == int(first_date[0]) else 1, int(last_date[1]) if year == int(last_date[0]) else 13):
        dates.append(f"{f'0{month}' if month in range(1, 10) else month}/{year}")


for i in range(len(dates)):
    date = dates[i]
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req=15/{date}"
    response = requests.get(url)
    current_df = pd.read_xml(response.text)
    filtered_df = current_df.loc[current_df['CharCode'].isin(cur_codes)]
    for cur in filtered_df['CharCode']:
        currency = 'BYR' if cur == 'BYN' else cur
        currencies[currency] = float(filtered_df[filtered_df['CharCode'] == cur]['Value'].values[0].replace(',', '.')) / float(
            filtered_df[filtered_df['CharCode'] == cur]['Nominal'].values[0])
    result.loc[i] = [date] + [currencies[cur] for cur in currencies]

result.to_csv("currencies.csv", index=False)
