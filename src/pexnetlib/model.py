from dataclasses import dataclass

@dataclass
class Device:
  ip: str
  username: str
  password: str
  enable: str
  device_type: str
