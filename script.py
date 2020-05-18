import argparse


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


def get_candidate_from_xls_file(path, str_numbers: list=None):
    # если файла не существует, или он не xls, или не тот формат - ошибка

    # результат:
    candidate = {
        'position': position,
        'name': name,
        'salary_expectations': salary_expectations,
        'comment': comment,
        'status': status,

        'cv_filepath': cv_filepath
        'str_number': str_number,
    }
    return candidate


if __name__ == "__main__":
    

    args = get_command_line_args()
    path = args.path
    access_token = args.access_token
    load_only_erroneous_lines = args.load_err
    print(path)
    print(access_token)
    print(load_only_erroneous_lines)
    
    str_numbers_list = None
    # if load_only_erroneous_lines:
    #     str_numbers_list = get_str_numbers_list_from_file() # эта функция удаляет временный файл

    while True:
        candidate = get_candidate_from_xls_file(path, str_numbers_list)
        if not candidate:
            break
        else:
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
