import statistics
import vacancies


class Program:
    def __init__(self):
        print('Добро пожаловать!')
        self.type = input('Выберите программу (Вакансии/Статистика): ')
        if self.type == 'Вакансии':
            self.inputConnect = vacancies.InputConnect()
        elif self.type == 'Статистика':
            self.report = statistics.Report()
        else:
            print('Некорректная программа!')


program = Program()
