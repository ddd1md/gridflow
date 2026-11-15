import argparse
import datetime
import json
import uuid


CUSTOM_NAMESPACE = uuid.UUID("3b12f1df-5232-4804-897e-917bf397618a")


def main(device_id=None, date=None):
    if device_id is None or date is None:
        print("Enter existing values.")

    dt_obj = datetime.datetime.fromisoformat(date)
    dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc)
    step = datetime.timedelta(hours=1)

    interval_kwh = 0
    voltage_v = 220.0
    current_a = 0.15
    frequncy_hz = 50.0

    for hour in range(1, 25):
        date_str = dt_obj.isoformat()
        interval_kwh = hour

        generate_dict = {
            "event_id": str(uuid.uuid5(namespace=CUSTOM_NAMESPACE, name=f"{device_id}+{date_str}")),
            "schema_version": 1,
            "device_id": int(device_id),
            "event_time": date_str,
            "ingest_time": date_str,
            "interval_kwh": float(interval_kwh),
            "voltage_v": voltage_v,
            "current_a": current_a,
            "frequency_hz": frequncy_hz
        }

        print(json.dumps(generate_dict))
        dt_obj += step


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="DataGenerator",
        description="Generate 24 JSON files (1 for each hour of the day) according to the specified schema: meter.v1.example.json."
    )

    parser.add_argument("-dId", "--device_id", help="Enter device_id > 0")
    parser.add_argument("-d", "--date", help="Enter date, example 2026-11-20")

    args = parser.parse_args()

    main(device_id=args.device_id, date=args.date)
