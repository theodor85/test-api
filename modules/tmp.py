''' В этом модуле реализована работа с временным файлом: сохранение
номеров строк ошибочных позиций и их получение из временного файла.
'''

import os


TMP_FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/err_strings.tmp'


def write_to_file_str_number(str_number):
    ''' Сохраняет ошибочные позиции во временный файл '''
    mode = 'a'
    if not os.path.exists(TMP_FILENAME):
        mode = 'w'
    with open(TMP_FILENAME, mode) as file:
        file.write(str(str_number)+'\n')

def get_str_numbers_list_from_file():
    ''' Получает ошибочные позиции из временного файла '''
    str_numbers_list = list()
    if not os.path.exists(TMP_FILENAME):
        return None
    with open(TMP_FILENAME, 'r') as file:
        for line in file:
            str_numbers_list.append(int(line))
    os.remove(TMP_FILENAME)
    return str_numbers_list