import argparse
import os
# это исключение возникает при неправильном формате excel-файла:
from zipfile import BadZipFile

from openpyxl import load_workbook

from working_with_the_api import send_applicant
from working_with_the_api import REQUEST_SUCCESS, REQUEST_ERROR


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description='Loads info about applicants from xls and sends to huntflow.')

    parser.add_argument('path', type=str, help='Path for xls-file')
    parser.add_argument('access_token', type=str, 
        help='Your personal access token for huntflow API')
    parser.add_argument('-l', '--load_err', action='store_true', 
        help='Use this flag for repeated loading the erroneous positions only.')
    
    args = parser.parse_args()
    return args


def get_cv_filepath(xls_path, position, name):
    ''' Путь к резюме определяем относительно пути к xls-файлу,
    сопостоявляем папку с должностью, а имя файла - с ФИО
    '''
    
    # получить папку
    base_folder = os.path.dirname(xls_path)

    # найти папку с именем position
    position_folder = ''
    for _, dirs, _ in os.walk(base_folder):  
        for dir in dirs:
            if dir==position:
                position_folder = base_folder + '/' + dir
                break
    
    if not position_folder:
        return None
    
    # найти файл резюме
    cv_filename = ''
    for _, _, files in os.walk(position_folder):  
        for file in files:
            if file[:5]==name[:5]: 
                cv_filename = position_folder + '/' + file
                break
 
    return cv_filename


def get_applicant_from_xls_file(path, str_numbers: list=None):
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
            'salary_expectations': str(worksheet['C'+str(i)].value),
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

    print('-'*30)
    for applicant in get_applicant_from_xls_file(path, str_numbers_list):
        print(f'\tЗагружается кандидат: {applicant["name"]}')
        status = send_applicant(applicant, access_token)
        if status==REQUEST_SUCCESS:
            continue
        else:
            print(f'Не выгружена строка {applicant["str_number"]}!')
            #write_to_file_str_number(applicant["str_number"])
    
    print('-'*30)
    print('Готово')
