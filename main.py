import statistics
import vacancies


class Program:
    """Класс для выбора и запуска программы.

    Attributes:
        type (string): Тип программы (Вакансии/Статистика)
        program (InputConnect or Report): Выбранная программа
    """
    def __init__(self):
        """Инициализирует объект Program, валидирует выбор программы.

        """
        print('Привет!')
        self.type = input('Выберите программу (Вакансии/Статистика): ')
        if self.type == 'Вакансии':
            self.program = vacancies.InputConnect()
        elif self.type == 'Статистика':
            self.program = statistics.Report()
        else:
            print('Некорректная программа!')


program = Program()
