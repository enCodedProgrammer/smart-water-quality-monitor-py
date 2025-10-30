# Smart Water Monitoring System (ESP32 + MicroPython)
# Reads Temperature, pH, and DO levels
# Publishes via MQTT to your broker

import network
import time
from umqtt.simple import MQTTClient
import machine
import onewire, ds18x20

# ---------- MQTT CONFIG ----------
MQTT_BROKER = "broker.hivemq.com"  # or your broker
CLIENT_ID = "esp32_water_monitor"
TOPIC = b"smartfarm/water"

# ---------- WIFI CONFIG ----------
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# ---------- SENSOR PINS ----------
# DS18B20 Temperature
temp_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(temp_pin))

# Analog sensors for pH and DO
ph_pin = machine.ADC(machine.Pin(34))
ph_pin.atten(machine.ADC.ATTN_11DB)  # for full 0–3.3V range
do_pin = machine.ADC(machine.Pin(35))
do_pin.atten(machine.ADC.ATTN_11DB)

# ---------- CONNECT TO WIFI ----------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected:", wlan.ifconfig())
    return wlan

# ---------- MQTT PUBLISH ----------
def publish_data(temp, ph, do):
    data = {
        "temperature": temp,
        "ph": ph,
        "dissolved_oxygen": do
    }
    msg = str(data)
    client.publish(TOPIC, msg)
    print("Published:", msg)

# ---------- MAIN LOOP ----------
def main():
    wlan = connect_wifi()
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.connect()
    print("Connected to MQTT broker")

    roms = ds_sensor.scan()
    print("Found DS18B20 devices:", roms)

    while True:
        ds_sensor.convert_temp()
        time.sleep_ms(750)

        # Get temperature reading
        if roms:
            temp = ds_sensor.read_temp(roms[0])
        else:
            temp = 25.0  # fallback if no sensor

        # Get analog readings (simulate calibration)
        ph_value = (ph_pin.read() / 4095) * 14  # range: 0–14
        do_value = (do_pin.read() / 4095) * 20  # range: 0–20 mg/L

        publish_data(round(temp, 2), round(ph_value, 2), round(do_value, 2))
        time.sleep(5)

# ---------- RUN ----------
try:
    main()
except KeyboardInterrupt:
    print("Stopped by user")
