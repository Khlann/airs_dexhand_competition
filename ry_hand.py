import asyncio
import struct
from time import sleep
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic 


notification_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
write_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
device_addr = "D0:6D:9E:B2:F7:FD"#第一次运行需要在这里找到设备，然后填入

action_tab = [
    # 大拇指           食指            中指            无名指        小指
    [4095, 4095, 4095, 0, 0, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095],
    # [3829, 3867, 3458, 4015, 4046, 4013, 4034, 3964, 4010, 4043, 3840, 3990, 867, 497, 887]
]
class BLEController:
    def __init__(self):
        # Device config
        self.notification_characteristic = notification_characteristic
        self.write_characteristic = write_characteristic
        self.device_addr = device_addr
        self.client = None
        # self.disconnected_event = asyncio.Event()
        
        # Initialize connection
        # self._connect()
    async def find_device(self):
        devices = await BleakScanner.discover()
        for device in devices:
            print("Device Name:", device.name)
            print("Device Address:", device.address)
        device = await BleakScanner.find_device_by_address(
            self.device_addr, cb=dict(use_bdaddr=False)
        )
    
    async def _connect(self):

        # 先尝试停止所有正在进行的扫描
        # await BleakScanner.stop(self)
        
        # 添加短暂延迟
        devices = await BleakScanner.discover()
        for device in devices:
            print("Device Name:", device.name)
            print("Device Address:", device.address)
        device = await BleakScanner.find_device_by_address(
            self.device_addr, cb=dict(use_bdaddr=False)
        )

        if device is None:
            print(f"Could not find device with address '{self.device_addr}'")
            return

        print("Connecting to device...")
        self.client = BleakClient(device)
        await self.client.connect()
        print("Connected")


    async def send_data(self):
        if not self.client or not self.client.is_connected:
            print("Not connected to device")
            return
            
        for i in range(15):
            data_15 = [action_tab[0][i], 1000, 70]
            data = self.pack_data(i+1, 0xAA, data_15)
            await self.client.write_gatt_char(self.write_characteristic, data)
            sleep(0.001)

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        print("rev data:", data)

    def pack_data(self, txid, cmd, data_15):
        packed_head = struct.pack('<B', 0xA5)
        packed_id = struct.pack('<H', txid)
        
        txlen = len(data_15) * 2 + 1
        packed_len = struct.pack('<B', txlen)
        
        packed_dat = struct.pack('<B', cmd & 0xff)
        for i in range(len(data_15)):
            packed_dat = packed_dat + struct.pack('<h', data_15[i])
        packed_all = packed_head + packed_id + packed_len + packed_dat
        
        checksum = sum(packed_all) & 0xFF
        packed_check = struct.pack('<B', checksum)
        
        return packed_all + packed_check

# Example usage
async def main():
    controller = BLEController()
    # await controller.find_device()#第一次运行需要在这里找到设备
    await controller._connect()
    await controller.send_data()
    await controller.disconnect()

if __name__ == '__main__':
    # 只创建一个事件循环
    asyncio.run(main())