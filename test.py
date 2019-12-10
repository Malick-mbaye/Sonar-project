import can

bus=can.interface.Bus(channel='slcan0', bustype='socketcan_native')
msg=can.Message(arbitration_id=0x53D,
                data=[0, 0, 0, 0, 12, 10, 0, 0],
                extended_id=False)
bus.send(msg)