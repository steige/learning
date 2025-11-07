import Adafruit_DHT

sensor = Adafruit_DHT.DHT11

pin = 14

while True:
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
  temperature = temperature * 9/5.0 + 32
  print ("Humidity:", humidity, "Temp:", temperature)

