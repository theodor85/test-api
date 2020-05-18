import argparse
import os
from zipfile import BadZipFile

from openpyxl import load_workbook


SUCCESS = 1
ERROR = 0




def get_command_line_args():
    parser = argparse.ArgumentParser(
        description='Loads info about candidates from xls and sends to huntflow.')

    parser.add_argument('path', type=str, help='Path for xls-file')
    parser.add_argument('access_token', type=str, 
        help='Your personal access token for huntflow API')
    parser.add_argument('-l', '--load_err', action='store_true', 
        help='Use this flag for repeated loading the erroneous positions only.')
    
    args = parser.parse_args()
    return args


def get_cv_filepath(xls_path, position, name):
    ''' Путь к резюме определяем относитель но пути к xls-файлу,
    сопостоявляем папку с должностью, а имя файла - с ФИО
    '''
    return '/home/theodor/progs/Python/projects1/test_api/Тестовое задание/Менеджер по продажам/Корниенко Максим.doc'


def get_candidate_from_xls_file(path, str_numbers: list=None):
    # если путь к файлу некорректный - ошибка
    if not ( os.path.exists(path) and os.path.isfile(path) ):
        print('ERROR: file not found!')
        return
    # если это не excel-файл - ошибка
    if not (os.path.splitext(path)[1] in ['.xls', '.xlsx']):
        print('ERROR: file is not in excel format!')
        return

    # загружаем из файла
    try:
        workbook = load_workbook(filename = path)
    except BadZipFile:
        print('ERROR: Bad excel-file format!')
        return
    
    worksheet = workbook.active

    i = 1
    while True:
        i += 1
        position = worksheet['A'+str(i)].value
        if not position:
            break
        cv_filepath = get_cv_filepath(
            xls_path=path, position=position, name=worksheet['B'+str(i)].value)
        yield {
            'position': position,
            'name': worksheet['B'+str(i)].value,
            'salary_expectations': worksheet['C'+str(i)].value,
            'comment': worksheet['D'+str(i)].value,
            'status': worksheet['E'+str(i)].value,
            'cv_filepath': cv_filepath,
            'str_number': i,
        }


if __name__ == "__main__":
    

    args = get_command_line_args()
    path = args.path
    access_token = args.access_token
    load_only_erroneous_lines = args.load_err
    
    str_numbers_list = None
    # if load_only_erroneous_lines:
    #     str_numbers_list = get_str_numbers_list_from_file() # эта функция удаляет временный файл

    print('*'*30)
    for candidate in get_candidate_from_xls_file(path, str_numbers_list):
        print(candidate)



    # while True:
    #     candidate = get_candidate_from_xls_file(path, str_numbers_list)
    #     if not candidate:
    #         break
    #     status = send_candidate(candidate, access_token)
    #     if status==SUCCESS:
    #         continue
    #     else:
    #         write_to_file_str_number(candidate["str_number"])
