class FlamengoTicketingError(Exception):
    """Erro base da automação de ingressos do Flamengo."""


class ParsingError(FlamengoTicketingError):
    """Erros de parsing de HTML/JSON."""


class LoginError(FlamengoTicketingError):
    """Falha de login."""


class TermsNotAcceptedError(LoginError):
    """Usuário não aceitou termos de uso na plataforma."""


class RequestError(FlamengoTicketingError):
    """Erros relacionados a requisições HTTP."""


class BookingError(FlamengoTicketingError):
    """Erros relacionados à reserva de ingressos."""
