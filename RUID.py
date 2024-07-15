import secrets
import time

class IDGenerator:
    def __init__(self, device_id):
        self.prefix = 0x0000
        self.version = 0X0
        self.device_id = device_id
        
        # 各フィールドのサイズ
        self.PREFIX_SIZE = 16
        self.VERSION_SIZE = 4
        self.DEVICE_ID_SIZE = 16
        self.TIMESTAMP_SIZE = 48
        self.RANDOM_SIZE = 44

        # シフト量の計算を事前に
        self.PREFIX_SHIFT = 128 - self.PREFIX_SIZE
        self.VERSION_SHIFT = self.PREFIX_SHIFT - self.VERSION_SIZE
        self.DEVICE_ID_SHIFT = self.VERSION_SHIFT - self.DEVICE_ID_SIZE
        self.TIMESTAMP_SHIFT = self.DEVICE_ID_SHIFT - self.TIMESTAMP_SIZE

    def generate_id(self, prefix = None, device_id = None):

        if not(prefix):
            prefix = self.prefix

        if not(device_id):
            device_id = self.device_id

        # 現在のタイムスタンプ（ミリ秒）
        timestamp = int(time.time() * 1000) & ((1 << self.TIMESTAMP_SIZE) - 1)
        
        # 暗号論的疑似乱数
        rand = secrets.randbits(self.RANDOM_SIZE)
        
        # 各フィールドをシフトして結合
        id_value = (
            (prefix << self.PREFIX_SHIFT) |
            (self.version << self.VERSION_SHIFT) |
            (device_id << self.DEVICE_ID_SHIFT) |
            (timestamp << self.TIMESTAMP_SHIFT) |
            rand
        )
        
        # 16進数形式に変換
        hex_id = hex(id_value)[2:].zfill(32)
        
        return hex_id

