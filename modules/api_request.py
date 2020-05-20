''' Модуль используется api.py и предоставляет отдельные классы для 
выполнения конкретных низкоуровневых дествий с API. 
Классы организованы по паттерну TemplateMethod
'''
import json
import subprocess
from abc import ABC, abstractmethod

import requests
from requests.exceptions import RequestException

REQUEST_SUCCESS = 1
REQUEST_ERROR = 0

USER_AGENT = 'App/1.0 (test@huntflow.ru)'
BASE_URL = 'https://dev-100-api.huntflow.ru'
ACCOUNT_ID = 6 # аккаут тестовой фирмы


class AbstractAccessorAPI(ABC):
    ''' Базовый абстрактный класс из паттерна TemplateMethod '''
    
    def __init__(self, applicant, access_token):
        self.applicant = applicant
        self.access_token = access_token

    def api_request(self) -> int:
        ''' Возвращает статус запроса: успех/ошибка
        '''
        # сделать url
        url = self._make_url()

        # подготовить тело запроса 
        body = self._make_body()

        # выполнить запрос
        response = self._request(url, body)

        # проверить, что ответ не пустой
        if not response:
            return REQUEST_ERROR

        # проверить, есть ли ошибки
        if response.get('errors'):
            print(f'ERROR: {response["errors"]}')
        else:
            # если нет - найти нужный параметр
            self._find_parameter(response)
            return REQUEST_SUCCESS

    def _headers(self):
        return {
            'User-Agent': USER_AGENT,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': '*/*',
        }

    @abstractmethod
    def _make_url(self):
        pass

    @abstractmethod
    def _make_body(self):
        pass 

    @abstractmethod
    def _request(self, url, body=None):
        pass

    @abstractmethod
    def _find_parameter(self, response):
        pass


class CV_Uploader(AbstractAccessorAPI):
    ''' Загрузка файла с резюме '''

    def __init__(self, applicant, access_token, filepath):
        super().__init__(applicant, access_token)
        self.filepath = filepath

    def _make_url(self):
        return f'{BASE_URL}/account/{ACCOUNT_ID}/upload'
    
    def _make_body(self):
        return None
    
    def _request(self, url, body=None):
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
        cmd_list.append(f'file=@{self.filepath}')
        cmd_list.append(url)
        result = subprocess.run(cmd_list, capture_output=True)        
        return json.loads(result.stdout.decode("utf-8"))
    
    def _find_parameter(self, response):
        self.applicant['id_cv'] = response['id']


class VacancyIdGetter(AbstractAccessorAPI):
    ''' Получение id вакансии данного кандидата '''

    def __init__(self, applicant, access_token, ):
        super().__init__(applicant, access_token)

    def _make_url(self):
        return f'{BASE_URL}/account/{ACCOUNT_ID}/vacancies'
    
    def _make_body(self):
        return None
    
    def _request(self, url, body=None):
        try:
            response = requests.get(url, headers=self._headers())
        except RequestException as exception:
            print(f'ERROR: VacancyIdGetter: {str(exception)}')
            return None
        else:
            try:
                result = response.json()
            except json.decoder.JSONDecodeError as exception:
                print('ERROR: VacancyIdGetter: JSON decode error!')
                return None
            else: 
                return result

    def _find_parameter(self, response):
        is_not_vacancy_found = True
        for vacancy in response['items']:
            if vacancy['position']==self.applicant['position']:
                self.applicant['vacancy_id'] = vacancy['id']
                is_not_vacancy_found = False
                break
        if is_not_vacancy_found:
            self.applicant['vacancy_id'] = None
            print(f'WARNING: Vacancy {self.applicant["position"]} not found!')
