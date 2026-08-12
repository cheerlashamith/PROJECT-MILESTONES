import pandas as pd
import os

FILE = "attendance.csv"

def save_attendance(record):

    df = pd.DataFrame([record])

    if os.path.exists(FILE):
        df.to_csv(
            FILE,
            mode="a",
            header=False,
            index=False
        )
    else:
        df.to_csv(
            FILE,
            index=False
        )


def load_attendance():

    if os.path.exists(FILE):
        return pd.read_csv(FILE)

    return pd.DataFrame(
        columns=[
            "Project ID",
            "Worker Name",
            "Date",
            "Time",
            "Status"
        ]
    )