import requests


class httpRequest:
    """Clase para manejar sesiones y solicitudes HTTP."""

    def __init__(self, user_agent):
        """Inicializa una instancia de HttpRequest con un agente de usuario dado."""
        self.session = self.create_session(user_agent)

    def create_session(self, user_agent):
        session = requests.Session()
        session.headers.update({"User-Agent": user_agent})
        return session
