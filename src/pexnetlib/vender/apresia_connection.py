from pexnetlib.base_connection import BaseConnection
from pexnetlib.async_base_connection import AsyncBaseConnection

class ApresiaConnection(BaseConnection):
    def __init__(
        self, device, timeout, use_username, login_prompt="login"
    ) -> None:
        super().__init__(
            device,
            timeout=timeout,
            use_username=use_username,
            login_prompt=login_prompt,
        )

class ApresiaConnectionAsync(AsyncBaseConnection):
    def __init__(
        self, device, timeout, use_username, login_prompt="login"
    ) -> None:
        super().__init__(
            device,
            timeout=timeout,
            use_username=use_username,
            login_prompt=login_prompt,
        )