''' Скрипт для загрузки данных о кандидатах из xls-файла
    в базу данных huntflow.
'''

import os

from modules.api import send_applicant
from modules.api import REQUEST_SUCCESS, REQUEST_ERROR
from modules.excel import get_applicant_from_xls_file
from modules.args import get_command_line_args


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


if __name__ == "__main__":

    args = get_command_line_args()
    path = args.path
    access_token = args.access_token
    load_only_erroneous_lines = args.load_err

    str_numbers_list = None
    if load_only_erroneous_lines:
        str_numbers_list = get_str_numbers_list_from_file()
    else:
        if os.path.exists(TMP_FILENAME):
            os.remove(TMP_FILENAME)

    print('-'*30)
    for applicant in get_applicant_from_xls_file(path, str_numbers_list):
        print(f'\tЗагружается кандидат: {applicant["name"]}')
        status = send_applicant(applicant, access_token)
        if status == REQUEST_SUCCESS:
            continue
        else:
            print(f'Не выгружена строка {applicant["str_number"]}!')
            write_to_file_str_number(applicant["str_number"])

    print('-'*30)
    print('Готово')
