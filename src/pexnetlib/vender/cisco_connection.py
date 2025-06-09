from pexnetlib.base_connection import BaseConnection
from pexnetlib.async_base_connection import AsyncBaseConnection

class CiscoConnection(BaseConnection):
    def __init__(self, device, use_username, timeout) -> None:
        super().__init__(
            device=device, use_username=use_username, timeout=timeout
        )

    def initialize(self) -> None:
        self.send_command("terminal length 0")
        self.send_command("terminal exec prompt timestamp")

    def enable(self) -> None:
        self.send_command(f"enable", prompt=self.password_prompt)
        self.send_command(self.device.enable, prompt="#")
        self.hostname, self.prompt = self.find_prompt("#")

class CiscoConnectionAsync(AsyncBaseConnection):
    def __init__(self, device, use_username, timeout) -> None:
        super().__init__(
            device=device, use_username=use_username, timeout=timeout
        )

    async def initialize(self) -> None:
        await self.send_command("terminal length 0")
        await self.send_command("terminal exec prompt timestamp")

    async def enable(self) -> None:
        await self.send_command(f"enable", prompt=self.password_prompt)
        await self.send_command(self.device.enable, prompt="#")
        self.hostname, self.prompt = await self.find_prompt("#")