import argparse


def get_command_line_args():
    ''' Обрабатывает аргументы командной строки и возвращает их '''
    parser = argparse.ArgumentParser(
        description='Loads info about applicants from xls and sends to huntflow.')

    parser.add_argument('path', type=str, help='Path for xls-file')
    parser.add_argument('access_token', type=str,
        help='Your personal access token for huntflow API')
    parser.add_argument('-l', '--load_err', action='store_true',
        help='Use this flag for repeated loading the erroneous positions only.')

    args = parser.parse_args()
    return args