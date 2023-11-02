class ScraperError(Exception):
    """Clase base para errores relacionados con el web scraping."""


class HTTPRequestError(ScraperError):
    """Error relacionado con una solicitud HTTP fallida."""

    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Error en la solicitud HTTP: código de estado {status_code}")


class ParsingError(ScraperError):
    """Error relacionado con el análisis del contenido HTML."""
