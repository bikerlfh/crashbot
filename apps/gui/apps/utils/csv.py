import csv
import os


def write_data(
    *,
    file_name: str,
    data: list[dict[str, any]],
) -> None:
    file_exists = os.path.isfile(file_name)
    fieldnames = data[0].keys() if data else []

    with open(file_name, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow(row)


def read_data(file_name: str) -> list[dict[str, any]] | None:
    if not os.path.isfile(file_name):
        return None

    with open(file_name, mode="r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def write_data_truncate(*, file_name: str, data: list[dict[str, any]]) -> None:
    fieldnames = data[0].keys() if data else []
    with open(file_name, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
