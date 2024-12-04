import asyncio
import struct
from time import sleep
import time
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic 
from pynput import keyboard

# Device config
par_notification_characteristic="0000ffe1-0000-1000-8000-00805f9b34fb"
par_write_characteristic="0000ffe1-0000-1000-8000-00805f9b34fb"
par_device_addr="D0:6D:9E:B2:F7:FD"

# 定义二维数组 ActionTab2
ActionTab2 = [
    # 大拇指           食指            中指            无名指        小指
    [0, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095],  # 0 -- 全张
    # [4095, 4095, 800,  4095, 4095, 800,  4095, 4095, 800,  4095, 4095, 800,  4095, 4095, 800],   # 1 -- 指节
    [3829, 3867, 3458, 4015, 4046, 4013, 4034, 3964, 4010, 4043, 3840, 3990, 867, 497, 887 ]
]
# class ryhand():
#     def __init__(self):
#         self.par_notification_characteristic = par_notification_characteristic
#         self.par_write_characteristic = par_write_characteristic
#         self.par_device_addr = par_device_addr


#监听回调函数，此处为打印消息
def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    print("rev data:",data)



def myPackData( txid, cmd, data_15  ):  
    # 使用struct.pack进行封包，'i'表示整数（4字节），'d'表示双精度浮点数（8字节）  
    # '<'表示小端格式  
    packed_head = struct.pack( '<B', 0xA5 )
    packed_id = struct.pack( '<H', txid )
    
    txlen = len( data_15 ) * 2 + 1
    packed_len = struct.pack( '<B', txlen )
    
    packed_dat = struct.pack( '<B', cmd & 0xff )
    for i in range ( len(data_15) ):
        packed_dat = packed_dat + struct.pack( '<h', data_15[i] )
    packed_all = packed_head + packed_id + packed_len + packed_dat
    
    # 计算 packed_all 中所有字节的校验和
    checksum = 0
    for i in range( len(packed_all) ):
        checksum = checksum + packed_all[i]

    packed_check = struct.pack( '<B', checksum & 0xFF )
    
    return packed_all + packed_check

async def main():
    devices = await BleakScanner.discover()

    device = await BleakScanner.find_device_by_address(
        par_device_addr, cb=dict(use_bdaddr=False)  #use_bdaddr判断是否是MOC系统
    )

    if device is None:
        print("could not find device with address '%s'", par_device_addr)
        return

    #事件定义
    disconnected_event = asyncio.Event()

    #断开连接事件回调
    async def disconnected_callback(client):
        print("Disconnected callback called!")
        disconnected_event.set()

    print("connecting to device...")
    async with BleakClient(device,disconnected_callback=disconnected_callback) as client:
        print("Connected")
        for i in range(15):
            data_15 = [ ActionTab2[1][i], 1000,70 ] 
            data = myPackData(i+1, 0xAA, data_15)
            await client.write_gatt_char(par_write_characteristic, data) 
            sleep(0.001)

if __name__ == '__main__':
    asyncio.run(main())