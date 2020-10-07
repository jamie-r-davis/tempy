import time

import adafruit_dht
import board
from config import Config
from ISStreamer.Streamer import Streamer

dht = adafruit_dht.DHT22(board.D4)
streamer = Streamer(
    bucket_name=Config.BUCKET_NAME,
    bucket_key=Config.BUCKET_KEY,
    access_key=Config.ACCESS_KEY,
)


def get_reading():
    try:
        humidity = dht.humidity
        temp_c = dht.temperature
    except RuntimeError:
        print("RuntimeError...")
        return

    temp_f = temp_c * 9.0 / 5.0 + 32.0
    streamer.log("Temperature (F)", temp_f)
    streamer.log("Humidity (%)", humidity)
    streamer.flush()


if __name__ == "__main__":
    while True:
        get_reading()
        time.sleep(Config.READING_INTERVAL)
