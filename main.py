# https://www.tomshardware.com/how-to/lcd-display-raspberry-pi-pico
# https://github.com/octaprog7/SCD4x/blob/master/main.py
# https://www.circuitschools.com/how-to-use-adc-on-raspberry-pi-pico-in-detail-with-micropython-example/
# https://www.circuitschools.com/interfacing-16x2-lcd-module-with-raspberry-pi-pico-with-and-without-i2c/#google_vignette
# https://peppe8o.com/mq-2-with-raspberry-pi-pico-gas-sensor-wiring-and-micropython-code/
# https://stackoverflow.com/questions/59296623/micropython-get-correct-current-time
import utime
import gc
import ujson
import ubinascii
import rp2
import network
from scd4x_sensirion import SCD4xSensirion
from machine import I2C, Pin, RTC
from bus_service import I2cAdapter
from utime import sleep
from pico_i2c_lcd import I2cLcd

# import urequests as requests
# import usocket as socket
from simple import MQTTClient
from secrets import Secrets

gc.collect()   # Run a garbage collection like python
rtc = RTC()
a = utime.localtime()
rtc.datetime((a[0], a[1], a[2], a[6], a[3], a[4], a[5], 0))
print(a)
del a

if __name__ == '__main__':
    
    # create LCD1602
    i2c0 = I2C(0, scl=Pin(13), sda=Pin(12), freq=100000)
    I2C_ADDR0 = i2c0.scan()[0]
    lcd = I2cLcd(i2c0, I2C_ADDR0, 2, 16)
    lcd.backlight_on()
    lcd.blink_cursor_off()
    lcd.hide_cursor()
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("LCD Address:"+str(hex(I2C_ADDR0)))
    
    # create object SCD41
    i2c1 = I2C(1, sda=Pin(14), scl=Pin(15), freq=100000)
    I2C_ADDR1 = i2c1.scan()[0]
    adaptor = I2cAdapter(i2c1)
    sensor = SCD4xSensirion(adaptor)
    sensor.set_measurement(start=False, single_shot=False)
    SensorID = sensor.get_id()
    print("SCD Address:"+str(hex(I2C_ADDR1)))

    # Load login data from different file for safety reasons
    SSID = Secrets['SSID']
    PASS = Secrets['PassWord']
    server = Secrets['MQTTServer']
    ClientID = Secrets['MQTTClient']
    user = Secrets['MQTTUser']
    password = Secrets['MQTTPass']
    port = Secrets['Port']
    topic = Secrets['Topic']

    # create network over wifi
    # Set country to avoid possible errors
    rp2.country('TH')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASS)
    # See the MAC address in the wireless chip OTP
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        print('Waiting for connection...')
        utime.sleep(1)
    if wlan.status() != 3:
        # Handle connection error
        # Error meanings
        # 0  Link Down
        # 1  Link Join
        # 2  Link NoIp
        # 3  Link Up
        # -1 Link Fail
        # -2 Link NoNet
        # -3 Link BadAuth
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Network failed")
        sleep(3)
        # set default IP Address
        wlan.ifconfig(('192.168.1.151', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
        print('Wi-Fi connection failed')
        print('Set IP Address to default : [192.168.1.151', '255.255.255.0', '192.168.1.1', '8.8.8.8]')
        ip = wlan.ifconfig()[0]
        print('IP Address :', ip)
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Set to default")
        lcd.move_to(0, 1)
        lcd.putstr("Consult Admin!")
        sleep(3)
        pass
    else:
        print('Connected')
        wlan.ifconfig(('10.99.96.8', '255.255.248.0', '10.99.103.254', '8.8.8.8'))
        ip = wlan.ifconfig()[0]
        print('IP Address :', ip)
        print('mac Address :', mac)
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("NetworkConnected")
        lcd.move_to(0, 1)
        lcd.putstr(ip)
        sleep(3)
    # Try to connect to mqtt broker
    def connect():
        print('Connected to MQTT Broker: "%s"' % (server))
        Client = MQTTClient(ClientID, server, port, user, password, keepalive=60)
        Client.connect()
        return Client

    def reconnect():
        print('Failed to connect to MQTT broker, Reconnecting...')
        utime.sleep(5)
        Client.connect()

    try:
        Client = connect()
    except OSError as e:
        print(str(e), end='\n')
        try:
            reconnect()
        except Exception as e:
            print(str(e), end='\n')
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("MQTT Failed")
            lcd.move_to(0, 1)
            lcd.putstr("Consult Admin!")
        pass
    sleep(3)
    ID = hex(SensorID[0])[2:]+hex(SensorID[1])[2:]+hex(SensorID[2])[2:]

    print(f"Sensor ID 3  Word: {SensorID}")
    print(f"Sensor ID in HEX: {ID}")
    t_offs = 0.0
    # Warning: To change or read sensor settings, the SCD4x must be in idle mode!!!
    # Otherwise an EIO exception will be raised!
    # print(f"Set temperature offset sensor to {t_offs} Celsius")
    # sensor.set_temperature_offset(t_offs)
    t_offs = sensor.get_temperature_offset()
    print(f"Get temperature offset from sensor: {t_offs} Celsius")
    masl = 44   # default is 160, 44 is Phitsanulok masl
    # MASL is abbreviation of Meters Above Sea Level
    print(f"Set my place M.A.S.L. to {masl} meter")
    sensor.set_altitude(masl)
    masl = sensor.get_altitude()
    print(f"Get M.A.S.L. from sensor: {masl} meter")
    lcd.clear()
    line1="M.A.S.L. : "+str(masl)+'m.'
    lcd.move_to(0, 0)
    lcd.putstr(line1)
    sleep(3)

    # data ready
    if sensor.is_data_ready():
        print("Measurement data can be read!")  # Данные измерений могут быть прочитаны!
    else:
        print("Measurement data missing!")

    if sensor.is_auto_calibration():
        print("The automatic self-calibration is ON!")
    else:
        print("The automatic self-calibration is OFF!")

    sensor.set_measurement(start=True, single_shot=False)
    wt = sensor.get_conversion_cycle_time()
    print("Periodic measurement started")
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("SCD41 Calibrate")
    lcd.move_to(0, 1)
    lcd.putstr("Please wait...")
    utime.sleep_ms(wt)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Reading using")
    lcd.move_to(0, 1)
    lcd.putstr("Periodic mode")
    sleep(3)
    for i in range(5):
        co2, t, rh = sensor.get_meas_data()
        print(f"CO2: {co2}; T: {t}; RH: {rh}")
        line2 = "T=%.1f" % (t)+'\xDFC, RH='+"%.0f" % (rh)+'%'
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("CO2: %dPPM" % co2)
        lcd.move_to(0, 1)
        lcd.putstr(line2)
        utime.sleep_ms(wt)

    print(20*"*_")
    print("Reading using an iterator!")
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Reading using")
    lcd.move_to(0, 1)
    lcd.putstr("iterator mode.")
    sleep(3)
    for counter, items in enumerate(sensor):
        utime.sleep_ms(wt)
        if items:
            co2, t, rh = items
            print(f"CO2: {co2}; T: {t}; RH: {rh}")
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("CO2: %dPPM" % co2)
            lcd.move_to(0, 1)
            lcd.putstr(line2)            
            if 5 == counter:
                break
    print(20 * "*_")
    print("Using single shot mode!")
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("CalibrateSuccess")
    lcd.move_to(0, 1)
    lcd.putstr("Start to read...")
    sensor.set_measurement(start=False, single_shot=False)
    while True:
        sensor.set_measurement(start=False, single_shot=True, rht_only=False)
        utime.sleep_ms(3 * wt)      # 3x period
        co2, t, rh = sensor.get_meas_data()
        print(f"CO2: {co2}; T: {t}; RH: {rh}")
        line2 = "T=%.1f" % (t)+'\xDFC, RH='+"%.0f" % (rh)+'%'
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("CO2: %dPPM" % co2)
        lcd.move_to(0, 1)
        lcd.putstr(line2)
        sleep(3)
        # prepare datetime for MQTT
        curtime = utime.localtime()
        # curtime = ds.date_time()
        r = "{:02d}-{:02d}-{} {:02d}:{:02d}:{:02d}".format(curtime[0], curtime[1], curtime[2], curtime[3], curtime[4], curtime[5])
        message = sorted({'PublishIP': ip, 'PublishMac': mac, 'Date/Time':r, 'Temperature': "%.1f" % (t), 'Humidity': "%.0f" % (rh), 'CO2': co2}.items())
        msg = bytes(ujson.dumps(message), 'utf-8')
        try:
            Client.publish(topic, msg)
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Success to sent")
            lcd.move_to(0, 1)
            lcd.putstr("Message->Broker")
            sleep(3)
        except Exception as e:
            print(str(e), end='\n')
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("MQTT fail!")
            lcd.move_to(0, 1)
            lcd.putstr("Consult Admin!")
            sleep(2)
            try:
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("Try to connect")
                lcd.move_to(0, 1)
                lcd.putstr("WIFI")
                sleep(2)
                wlan.connect(SSID, PASS)
                if wlan.status() == 3:
                    wlan.ifconfig(('10.99.96.8', '255.255.248.0', '10.99.103.254', '8.8.8.8'))
                    # wlan.ifconfig(('192.168.1.151', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
                    ip = wlan.ifconfig()[0]
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr("WIFI Connected")
                    lcd.move_to(0, 1)
                    lcd.putstr(ip)
                    sleep(3)
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr("Try to connect")
                    lcd.move_to(0, 1)
                    lcd.putstr("MQTT Broker")
                    Client = connect()
                else:
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr("fail to connect")
                    lcd.move_to(0, 1)
                    lcd.putstr("WIFI network")
                sleep(3)
            except Exception as e:
                print('str(e)', end='\n')
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("fail to connect")
                lcd.move_to(0, 1)
                lcd.putstr("WIFI network")
                sleep(3)
            pass
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("CO2: %dPPM" % co2)
        lcd.move_to(0, 1)
        lcd.putstr(line2)