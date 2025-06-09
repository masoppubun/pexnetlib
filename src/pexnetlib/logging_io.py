import logging
from telnetlib3 import TelnetReaderUnicode
class LoggingIO:
    """pexpectのログ出力をロガーに吐き出すためのクラス"""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.buffer = ""

    def write(self, b: bytes) -> None:
        self.buffer += b.decode()

    def flush(self) -> None:
        if "\n" in self.buffer:
            self.logger.debug(self.buffer)
            self.buffer = ""

class AsyncLogginIO:
    """telnetlib3のTelnetReaderの出力をロガーに吐き出すためのクラス"""
    def __init__(self, reader: TelnetReaderUnicode, logger: logging.Logger):
        self._reader = reader
        self.logger = logger
        self.buffer = ""

    async def read(self, n: int = -1) -> str:
        data = await self._reader.read(n)
        self.buffer += data
        if "\n" in data:
            self.logger.debug(f"{self.buffer}")
            self.buffer = ""
        return data

    async def flush(self):
        if self.buffer:
            self.logger.debug(self.buffer)
            self.buffer = ""

    def at_eof(self) -> bool:
        return self._reader.at_eof()

    def __getattr__(self, name):
        return getattr(self._reader, name)