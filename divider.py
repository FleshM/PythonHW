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
