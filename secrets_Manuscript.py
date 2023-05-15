#for Login internal broker
Secrets = {
   'SSID'      : 'BP',
   'PassWord'  : '15935799',
   'timezone'  : 'Asia/Bangkok',
   'MQTTServer':'10.99.96.6',
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


