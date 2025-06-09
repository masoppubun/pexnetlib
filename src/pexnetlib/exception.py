class PexnetlibBaseException(Exception):
    pass

class AsyncExpectTimeoutException(PexnetlibBaseException):
    """exceptタイムアウト"""
    def __init__(self, buffer) -> None:
        self.buffer = buffer

    def __str__(self) -> str:
        output = f"""コマンドの実行がタイムアウトしました。\nlast_buffer_data:\n{self.buffer}"""
        return output

class ConnectionException(PexnetlibBaseException):
    """接続失敗"""

    def __init__(self, ipaddr, device_type) -> None:
        self.ipaddr = ipaddr
        self.device_type = device_type

    def __str__(self) -> str:
        return f"ホストへの接続に失敗 IP: {self.ipaddr} device_type: {self.device_type}"


class AuthenticationException(PexnetlibBaseException):
    """ログイン失敗"""

    def __init__(self, ipaddr, device_type) -> None:
        self.ipaddr = ipaddr
        self.device_type = device_type

    def __str__(self) -> str:
        return f"ホストへのログインに失敗 IP: {self.ipaddr} device_type: {self.device_type}"
