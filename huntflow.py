''' Скрипт для загрузки данных о кандидатах из xls-файла
    в базу данных huntflow.
'''
import os

from modules.api import send_applicant
from modules.api import REQUEST_SUCCESS, REQUEST_ERROR
from modules.excel import get_applicant_from_xls_file
from modules.args import get_command_line_args
from modules.tmp import get_str_numbers_list_from_file, write_to_file_str_number
from modules.tmp import write_to_file_str_number
from modules.tmp import TMP_FILENAME


if __name__ == "__main__":

    args = get_command_line_args()

    # если передан параметр -l (--load_err), то получить список строк,
    # ранее завершившихся с ошибкой
    str_numbers_list = None
    if args.load_err:
        str_numbers_list = get_str_numbers_list_from_file()
    else:
        # временный файл нужно удалить, т.к. при новом запуске в него будут
        # записываться новые данные
        if os.path.exists(TMP_FILENAME):
            os.remove(TMP_FILENAME)

    print('-'*30)
    for applicant in get_applicant_from_xls_file(args.path, str_numbers_list):
        print(f'\tЗагружается кандидат: {applicant["name"]}')
        status = send_applicant(applicant, args.access_token)
        if status == REQUEST_SUCCESS:
            continue
        else:
            print(f'Не выгружена строка {applicant["str_number"]}!')
            write_to_file_str_number(applicant["str_number"])

    print('-'*30)
    print('Готово')
