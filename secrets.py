#for Login internal broker
Secrets = {
   'SSID'      : 'MANEEWIFI',
   'PassWord'  : 'm6045001',
   'timezone'  : 'Asia/Bangkok',
   'MQTTServer':'192.168.1.149',
   'MQTTClient': 'PicoW',
   'MQTTUser'  : 'pico',
   'MQTTPass'  : 'picopassword',
   'Port'      : 1883,
   'Topic'     : 'FirstTopic'
}
'''
#for Login emqx.io
Secrets = {
   'SSID'      : 'ManeeWiFi',
   'PassWord'  : 'm6045001',
   'timezone'  : 'Asia/Bangkok',
   'MQTTServer':'broker.emqx.io',
   'MQTTClient': 'raspberry-pub-{time.time_ns()}',
   'MQTTUser'  : 'emqx',
   'MQTTPass'  : 'public',
   'Port'      : 8883
}
'''
