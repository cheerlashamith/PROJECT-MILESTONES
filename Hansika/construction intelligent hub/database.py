import pandas as pd
import os

FILE = "projects.csv"

def save_project(project):

    if os.path.exists(FILE):
        df = pd.read_csv(FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([project])], ignore_index=True)

    df.to_csv(FILE, index=False)


def load_projects():

    if os.path.exists(FILE):
        return pd.read_csv(FILE)

    return pd.DataFrame()