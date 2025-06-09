import re
from datetime import datetime, timedelta
from typing import Any, Union, Generator
from pexpect import spawn
from pexpect.exceptions import TIMEOUT

from pexnetlib.log import log
from pexnetlib.logging_io import LoggingIO
from pexnetlib.model import Device
from pexnetlib.textfsm_util import get_structured_data_textfsm
from pexnetlib.exception import ConnectionException, AuthenticationException


class AsyncBaseConnection:
    def __init__(
        self,
        device: Device,
        timeout=30,
        login_prompt="Username",
        use_username=True,
        password_prompt="assword",
        user_prompt=">",
        enable_prompt="#",
        hostname="",
        prompt="",
        crlf=False,
        ansi=False
    ) -> None:
        # クラス変数を定義
        self.device = device
        self.timeout = timeout
        self.login_prompt = login_prompt
        self.use_username = use_username
        self.password_prompt = password_prompt
        self.user_prompt = user_prompt
        self.enable_prompt = enable_prompt
        self.hostname = hostname
        self.prompt = prompt
        self.crlf = crlf
        self.ansi = ansi
        self.child = None

    def __await__(self) -> Generator[Any, None, "AsyncBaseConnection"]:
        async def wrapper() -> "AsyncBaseConnection":
            await self.telnet_initialize()
            return self
        return wrapper().__await__()
    
    async def __aenter__(self) -> "AsyncBaseConnection":
        await self.telnet_initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.disconnect()
    
    async def telnet_initialize(self) -> None:
        # 接続と初期化
        await self.connect()
        self.hostname, self.prompt = await self.find_prompt(self.user_prompt)
        await self.initialize()


    async def connect(self) -> None:
        self.child = spawn("telnet " + self.device.ip, timeout=self.timeout)
        loggingio = LoggingIO(log)
        self.child.logfile_read = loggingio

        try:
            # ログインにユーザネームが必要な場合
            if self.use_username:
                await self.expect(f"{self.login_prompt}", read_timeout=self.timeout)
            else:
                await self.expect(f"{self.password_prompt}", read_timeout=self.timeout)

        except TIMEOUT:
            # ログインプロンプトが返ってこないのはtelnet接続失敗と判断する
            raise ConnectionException(self.device.ip, self.device.device_type)

        if self.use_username:
            await self.sendline(self.device.username)
            await self.expect(f"{self.password_prompt}", read_timeout=self.timeout)

        await self.sendline(self.device.password)
        try:
            await self.expect(f"{self.user_prompt}", read_timeout=self.timeout)

        except TIMEOUT:
            # ユーザプロンプトが返ってこないのはログイン認証の失敗と判断する
            raise AuthenticationException(self.device.ip, self.device.device_type)


    async def sendline(self, command: str) -> None:
        # childが生成されている場合のみ
        if not self.child:
            raise RuntimeError

        if self.crlf:
            command = command + "\r\n"
        self.child.sendline(command)

    async def expect(self, pattern: str, read_timeout=30, reg=False) -> str:
        data = b""
        buffer = b""
        start = datetime.now()
        pattern_bytes = pattern.encode()

        # childが生成されている場合のみ
        if not self.child:
            raise RuntimeError

        while True:
            try:
                chunk = self.child.read_nonblocking(size=1024, timeout=1)
                if chunk:
                    data += chunk
                    buffer = (buffer + chunk)[-4096:]
                    start = datetime.now()
                    if reg:
                        if re.search(pattern, chunk):
                            break
                    else:
                        if pattern_bytes in chunk:
                            break

            except TIMEOUT:
                if datetime.now() - start > timedelta(seconds=read_timeout):
                    raise

                continue

        raw_data = data.decode(encoding="utf-8", errors="ignore")
        return raw_data

    async def find_prompt(self, current_prompt: str) -> tuple[str, str]:
        """ホスト名を含めたプロンプトを取得"""
        await self.sendline("")
        raw_data = await self.expect(current_prompt)
        hostname = self.sanitize_output(
            raw_data, command="", pattern=current_prompt, echo=True
        )
        prompt = hostname + current_prompt

        return hostname, prompt

    async def check_prompt(self, prompt_key: str) -> bool:
        """特定のモードへ移行できたか確認"""
        await self.sendline("")
        try:
            await self.expect(prompt_key)

        except TIMEOUT:
            return False

        return True

    async def initialize(self) -> None:
        """装置ログイン後に必要なコマンドを実行する"""
        # self.send_command('terminal length ')
        pass

    async def enable(self) -> None:
        """enableモードへ遷移する"""
        pass

    def sanitize_output(
        self, raw_data: str, command: str, pattern: str, echo: bool
    ) -> str:
        if self.ansi:
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[0-?*[ -/]*[@-~])")
            raw_data = ansi_escape.sub("", raw_data)

        if echo:
            raw_data = raw_data.replace(command, "")
            raw_data = (
                raw_data.replace(f"!{pattern}", "")
                .replace(f"!!{pattern}", "")
                .replace(pattern, "")
            )

        return raw_data.strip()

    async def send_command(
        self,
        command: str,
        use_textfsm: bool = False,
        read_timeout: int = 30,
        prompt: str = "",
        reg: bool = False,
    ) -> Union[str, list[Any], dict[str, Any]]:
        """コマンドを実行して結果を返却"""
        prompt_str = prompt or self.prompt
        await self.sendline(f"{command}")
        raw_data = await self.expect(f"{prompt_str}", read_timeout=read_timeout, reg=reg)
        raw_data = self.sanitize_output(
            raw_data, command=command, pattern=prompt_str, echo=True
        )

        if use_textfsm:
            return get_structured_data_textfsm(
                raw_data,
                platform=self.device.device_type,
                command=command,
                template=None,
            )

        return raw_data

    def disconnect(self) -> None:
        if self.child:
            self.child.close()
