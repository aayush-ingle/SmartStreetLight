import serial
import pandas as pd
from datetime import datetime
import os
import time

PORT = "COM3"
BAUD_RATE = 115200

CSV_FILE = "smart_street_light_dataset.csv"

print("Connecting to ESP32...")
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

time.sleep(2)

print("ESP32 connected!")
print("Data collection started.")
print("Press CTRL+C to stop.\n")

columns = [
    "date",
    "time",
    "day",
    "millis",
    "lux",
    "motion",
    "motion_count",
    "brightness",
    "night"
]

# Create CSV if it doesn't exist
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=columns).to_csv(
        CSV_FILE,
        index=False
    )

motion_count = 0
previous_motion = 0

try:

    while True:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if line.startswith("DATA,"):

            parts = line.split(",")

            if len(parts) == 5:

                millis = int(parts[1])
                lux = float(parts[2])
                motion = int(parts[3])
                brightness = int(parts[4])

                # Count a new motion event
                if motion == 1 and previous_motion == 0:
                    motion_count += 1

                previous_motion = motion

                # Current computer date/time
                now = datetime.now()

                date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")
                day = now.strftime("%A")

                # Day/night based on lux
                night = 1 if lux < 50 else 0

                data = {
                    "date": date,
                    "time": current_time,
                    "day": day,
                    "millis": millis,
                    "lux": lux,
                    "motion": motion,
                    "motion_count": motion_count,
                    "brightness": brightness,
                    "night": night
                }

                # Save immediately
                pd.DataFrame([data]).to_csv(
                    CSV_FILE,
                    mode="a",
                    header=False,
                    index=False
                )

                print(
                    f"{date} {current_time} | "
                    f"{day} | "
                    f"Lux: {lux:.2f} | "
                    f"Motion: {motion} | "
                    f"Motion Count: {motion_count} | "
                    f"Brightness: {brightness}"
                )

except KeyboardInterrupt:

    print("\nData collection stopped.")

finally:

    ser.close()
    print("ESP32 disconnected.")
    print("Dataset saved:", CSV_FILE)