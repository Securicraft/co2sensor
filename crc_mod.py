# https://github.com/octaprog7/SCD4x/blob/master/sensor_pack/crc_mod.py
"""CRC-8: 0x87
    CRC-8: 0x52"""

def crc8(sequence, polynomial: int, init_value: int = 0x00) -> int:
    mask = 0xFF
    crc = init_value & mask
    for item in sequence:
        crc ^= item & mask
        for _ in range(8):
            if crc & 0x80:
                crc = mask & ((crc << 1) ^ polynomial)
            else:
                crc = mask & (crc << 1)
    return crc

