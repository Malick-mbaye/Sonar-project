import can
bus=can.interface.Bus(channel='can0', bustype='socketcan_native')
msg=can.Message(arbitration_id=0x53D,
                data=[0, 0, 0,0 ,12 , 0, 0, 0],
                extended_id=False)
bus.send(msg)