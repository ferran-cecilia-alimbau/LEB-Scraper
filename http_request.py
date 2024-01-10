import requests
import logging

class HTTPRequest:
    '''Clase para manejar sesiones y solicitudes HTTP.'''

    timeout = 10  # Default timeout for HTTP requests

    def __init__(self, user_agent):
        '''Inicializa una instancia de HTTPRequest con un agente de usuario dado.'''
        self.session = self.create_session(user_agent)

    def create_session(self, user_agent):
        '''Crea y devuelve una sesión con el agente de usuario especificado.'''
        session = requests.Session()
        try:
            session.headers.update({'User-Agent': user_agent})
        except requests.RequestException as e:
            logging.error(f'Failed to update session headers: {e}')
            raise
        return session

    def make_request(self, url, method='get', **kwargs):
        '''Make an HTTP request using the specified method.'''
        supported_methods = {'get': self.session.get, 'post': self.session.post}
        if method not in supported_methods:
            logging.error(f'Unsupported HTTP method: {method}')
            raise ValueError(f'Unsupported HTTP method: {method}')
        logging.info(f'Making {method} request to {url}')
        try:
            response = supported_methods[method](url, timeout=self.timeout, **kwargs)
            response.raise_for_status()  # Raises HTTPError if the HTTP request returned an unsuccessful status code
            logging.info(f'Request to {url} successful with status code {response.status_code}')
        except requests.RequestException as e:
            logging.error(f'HTTP request to {url} failed: {e}')
            raise
        return response
