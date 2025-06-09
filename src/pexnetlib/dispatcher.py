from pexnetlib.CLASS_MAPPER import CLASS_MAPPER_SYNC, CLASS_MAPPER_ASYNC
from pexnetlib.model import Device
from pexnetlib.base_connection import BaseConnection
from pexnetlib.async_base_connection import AsyncBaseConnection

platforms = list(CLASS_MAPPER_SYNC.keys())
platforms.sort()

# 装置種別に該当しない場合の通知用
platforms_str = "\n".join(platforms)
platforms_str = "\n" + platforms_str

def ConnectHandler(device_dict: dict, timeout=30, use_username: bool = True) -> BaseConnection:
    device = Device(**device_dict)
    device_type = device.device_type

    if device_type not in platforms:
        raise ValueError(f"Unsupported device type: {device_type}")

    try:
        ConnectionClass = CLASS_MAPPER_SYNC[device_type]
        return ConnectionClass(device, timeout=timeout, use_username=use_username)
    
    except KeyError:
        raise ValueError(f"Unsupported device type: {device_type}")

def ConnectHandlerAsync(device_dict: dict, timeout=30, use_username: bool = True) -> AsyncBaseConnection:
    device = Device(**device_dict)
    device_type = device.device_type

    if device_type not in platforms:
        raise ValueError(f"Unsupported device type: {device_type}")

    try:
        ConnectionClass = CLASS_MAPPER_ASYNC[device_type]
        return ConnectionClass(device, timeout=timeout, use_username=use_username)
    
    except KeyError:
        raise ValueError(f"Unsupported device type: {device_type}")
