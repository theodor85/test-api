''' В этом модуле реализвана функциональность загрузки данных по huntflow API
'''

from .api_request import CV_Uploader, VacancyIdGetter, ApplicantDatabaseSaver
from .api_request import StatusIdGetter, ApplicantToVacancyBonding
from .api_request import REQUEST_ERROR, REQUEST_SUCCESS


class ApplicantSender:
    ''' Callable класс, в котором реализована логика отправки данных о 
    кандидате.
    '''

    def __call__(self, applicant, access_token):
        self.applicant = applicant
        self.access_token = access_token
        self._send()
        return self.status
    
    def _send(self):
        self._upload_cv()
        if self.status == REQUEST_ERROR:
            return

        self._get_vacancy_id()
        if self.status == REQUEST_ERROR:
            return

        self._add_applicant_to_database()
        if self.status == REQUEST_ERROR:
            return

        self._get_vacancy_status_id()       
        if self.status == REQUEST_ERROR:
            return

        self._add_applicant_to_vacancy()

    def _upload_cv(self):
        uploader = CV_Uploader(
            self.applicant, self.access_token, self.applicant['cv_filepath'])
        self.status = uploader.api_request()

    def _get_vacancy_id(self):
        vacancy_id_getter = VacancyIdGetter(self.applicant, self.access_token)
        self.status = vacancy_id_getter.api_request()

    def _add_applicant_to_database(self):
        saver = ApplicantDatabaseSaver(self.applicant, self.access_token)
        self.status = saver.api_request()
    
    def _get_vacancy_status_id(self):
        status_getter = StatusIdGetter(self.applicant, self.access_token)
        self.status = status_getter.api_request()

    def _add_applicant_to_vacancy(self):
        bonding = ApplicantToVacancyBonding(self.applicant, self.access_token)
        self.status = bonding.api_request()

send_applicant = ApplicantSender()
