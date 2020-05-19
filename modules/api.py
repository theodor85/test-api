''' В этом модуле реализвана функциональность для обращения к huntflow API
'''

import json
import subprocess

import requests
from requests.exceptions import RequestException

REQUEST_SUCCESS = 1
REQUEST_ERROR = 0

USER_AGENT = 'App/1.0 (test@huntflow.ru)'
BASE_URL = 'https://dev-100-api.huntflow.ru'
ACCOUNT_ID = 6 # аккаут тестовой фирмы

UPLOAD_CV_WARNING_MSG = 'WARNING: Не удалось загрузить резюме кандидата \
    {applicant} в строке {str_number}. Ошибка: {err}'
ERROR_MESSAGE_VACANCY = 'ERROR: Не удалось загрузить кандидата \
    {applicant} в строке {str_number}. Не найдена вакансия {vacancy}. Ошибка: {err}'
ERROR_MESSAGE_APPLICANT = 'ERROR: Не удалось загрузить кандидата \
    {applicant} в строке {str_number}. Ошибка: {err}'
ERROR_MESSAGE_VACANCY_STATUS = 'ERROR: Не удалось получить статус вакансии для \
    {applicant} в строке {str_number}. Ошибка: {err}'


def translate_statuses(status_rus):
    ''' Вспомогательная функция для перевода статуса кандидата
    с русского на английский '''
    
    data = {
        'Отправлено письмо': 'Submitted',
        'Интервью с HR': 'HR Interview',
        'Выставлен оффер': 'Offered',
        'Отказ': 'Declined',
    }
    return data.get(status_rus)

class ApplicantSender:
    ''' Callable класс, в котором реализована логика отправки данных о 
    кандидате.
    '''

    def __call__(self, applicant, access_token):
        self.applicant = applicant
        self.access_token = access_token
        self._make_headers()
        self._make_urls()
        self._send()
        return self.status
    
    def _make_headers(self):
        self.headers_applicants = {
            'User-Agent': USER_AGENT,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': '*/*',
        }
        self.headers_files = {
            'User-Agent': USER_AGENT,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': '*/*',
            'Content-Type': 'multipart/form-data',
            'X-File-Parse': 'true',
        }

    def _make_urls(self):
        self.url_applicants = f'{BASE_URL}/account/{ACCOUNT_ID}/applicants'
        self.url_files = f'{BASE_URL}/account/{ACCOUNT_ID}/upload'
        self.url_vacancies = f'{BASE_URL}/account/{ACCOUNT_ID}/vacancies'
        self.url_statuses = f'{BASE_URL}/account/{ACCOUNT_ID}/vacancy/statuses'
    
    def _send(self):
        self._upload_cv()
        if self.status==REQUEST_ERROR:
            return

        self._get_vacancy_id()
        if self.status==REQUEST_ERROR:
            return

        self._add_applicant_to_database()
        if self.status==REQUEST_ERROR:
            return

        self._get_vacancy_status_id()       
        if self.status==REQUEST_ERROR:
            return

        self._add_applicant_to_vacancy()

    def _upload_cv(self):
        response = self._upload_file(
            url=self.url_files,
            filepath=self.applicant['cv_filepath'],
        )
        if not response:
             self.applicant['id_cv'] = None
             self.status = REQUEST_ERROR
             return

        if response.get('errors'):
            self.applicant['id_cv'] = None
            print(UPLOAD_CV_WARNING_MSG.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err=str(response['errors']),
            ))
            self.status = REQUEST_ERROR
        else:
            self.applicant['id_cv'] = response['id']
            self.status = REQUEST_SUCCESS

    def _upload_file(self, url, filepath):
        ''' Загружам файл с помощью curl '''
        cmd_list = []
        cmd_list.append('curl')
        cmd_list.append('-X')
        cmd_list.append('POST')
        cmd_list.append('-H')
        cmd_list.append('Content-Type: multipart/form-data')
        cmd_list.append('-H')
        cmd_list.append('X-File-Parse: true')
        cmd_list.append('-H')
        cmd_list.append(f'Authorization: Bearer {self.access_token}')
        cmd_list.append('-F')
        cmd_list.append(f'file=@{filepath}')
        cmd_list.append(url)
        result = subprocess.run(cmd_list, capture_output=True)        
        return json.loads(result.stdout.decode("utf-8"))

    def _do_post_request(self, url, headers, body, error_msg):
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
        except RequestException as exception:
            print(error_msg.format(err=str(exception)))
            return None
        else:
            return response.json()

    def _get_vacancy_id(self):
        response = self._do_get_request(
            url=self.url_vacancies,
            headers=self.headers_applicants, 
            error_msg=ERROR_MESSAGE_VACANCY.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                vacancy=self.applicant['position'],
                err='',
            )
        )
        if not response:
             self.status = REQUEST_ERROR
             return

        if response.get('errors'):
            print(ERROR_MESSAGE_VACANCY.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err=str(response['errors']),
                vacancy=self.applicant['position'],
            ))
            self.status = REQUEST_ERROR
            return
        is_not_vacancy_found = True
        for vacancy in response['items']:
            if vacancy['position']==self.applicant['position']:
                self.applicant['vacancy_id'] = vacancy['id']
                is_not_vacancy_found = False
                break
        if is_not_vacancy_found:
            self.status = REQUEST_ERROR
        else:
            self.status = REQUEST_SUCCESS

    def _do_get_request(self, url, headers, error_msg):
        try:
            response = requests.get(url, headers=headers)
        except RequestException as exception:
            print(error_msg.format(err=str(exception)))
            return None
        else:
            try:
                result = response.json()
            except json.decoder.JSONDecodeError as exception:
                print(error_msg.format(err=str(exception)))
                return None
            else: 
                return result

    def _add_applicant_to_database(self):
        body = {
                "last_name": self.applicant['name'].split()[0],
                "first_name": self.applicant['name'].split()[1],
                "money": self.applicant['salary_expectations'],
            }
        if self.applicant.get('id_cv'):
            body['externals'] = [
                {
                    "auth_type": "NATIVE",
                    "files": [
                        {
                            "id": self.applicant['id_cv'],
                        }
                    ],
                }
            ]
        response = self._do_post_request(
            url=self.url_applicants, headers=self.headers_applicants,
            body=body,
            error_msg=ERROR_MESSAGE_APPLICANT.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err='',
            )
        )
        if not response:
            self.status = REQUEST_ERROR
            return

        if response.get('errors'):
            print(ERROR_MESSAGE_APPLICANT.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err=str(response['errors']),
            ))
            self.status = REQUEST_ERROR
        else:
            self.applicant['id_applicant'] = response['id']
            self.status = REQUEST_SUCCESS
    
    def _get_vacancy_status_id(self):
        response = self._do_get_request(url=self.url_statuses,
            headers=self.headers_applicants,
            error_msg=ERROR_MESSAGE_VACANCY_STATUS.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err='',
            )
        )
        if not response:
             self.status = REQUEST_ERROR
             return

        if response.get('errors'):
            print(ERROR_MESSAGE_VACANCY_STATUS.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err=str(response['errors']),
            ))
        is_not_status_found = True
        for status in response['items']:
            if status['name'] == translate_statuses(self.applicant['status']):
                self.applicant['status_id'] = status['id']
                is_not_status_found = False
                break
        if is_not_status_found:
            self.status = REQUEST_ERROR
        else:
            self.status = REQUEST_SUCCESS

    def _add_applicant_to_vacancy(self):
        body = {
            "vacancy": self.applicant['vacancy_id'],
            "status": self.applicant['status_id'],
            "comment": self.applicant['comment'],
            "files": [
                {
                    "id": self.applicant['id_cv']
                },
            ],
        }
        response = self._do_post_request(
            url=f'{BASE_URL}/account/{ACCOUNT_ID}/applicants/{self.applicant["id_applicant"]}/vacancy',
            headers=self.headers_applicants,
            body=body,
            error_msg=ERROR_MESSAGE_APPLICANT.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err='',
            )
        )
        if not response:
            self.status = REQUEST_ERROR
            return
        if response.get('errors'):
            print(str(response['errors']))
            print(ERROR_MESSAGE_APPLICANT.format(
                applicant=self.applicant['name'],
                str_number=self.applicant['str_number'],
                err=str(response['errors']),
            ))
            self.status = REQUEST_ERROR
        else:
            self.status = REQUEST_SUCCESS

send_applicant = ApplicantSender()
