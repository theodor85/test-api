''' В этом модуле реализвана функциональность загрузки данных по huntflow API
'''

import json
import subprocess

import requests
from requests.exceptions import RequestException

from .api_request import CV_Uploader, VacancyIdGetter, ApplicantDatabaseSaver
from .api_request import StatusIdGetter, ApplicantToVacancyBonding

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
        uploader = CV_Uploader(
            self.applicant, self.access_token, self.applicant['cv_filepath'])
        self.status = uploader.api_request()

    def _do_post_request(self, url, headers, body, error_msg):
        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
        except RequestException as exception:
            print(error_msg.format(err=str(exception)))
            return None
        else:
            return response.json()

    def _get_vacancy_id(self):
        vacancy_id_getter = VacancyIdGetter(self.applicant, self.access_token)
        self.status = vacancy_id_getter.api_request()

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
        saver = ApplicantDatabaseSaver(self.applicant, self.access_token)
        self.status = saver.api_request()
    
    def _get_vacancy_status_id(self):
        status_getter = StatusIdGetter(self.applicant, self.access_token)
        self.status = status_getter.api_request()

    def _add_applicant_to_vacancy(self):
        bonding = ApplicantToVacancyBonding(self.applicant, self.access_token)
        self.status = bonding.api_request()
        
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
