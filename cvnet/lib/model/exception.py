from homeassistant.exceptions import HomeAssistantError


class UnauthorizedException(HomeAssistantError):
    """Exception raised for unauthorized access."""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class AuthenticationFailedException(HomeAssistantError):
    """Exception raised for authentication failures."""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class UnknownException(HomeAssistantError):
    """Exception raised for unknown errors."""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

