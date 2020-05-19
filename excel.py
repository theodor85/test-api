import os
# это исключение возникает при неправильном формате excel-файла:
from zipfile import BadZipFile

from openpyxl import load_workbook


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
        # если загружаем указанные строки, проверяем вхождение строки
        # в список указанных строк (иначе - следующая итерация)
        if str_numbers:
            if not (i in str_numbers):
                continue

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