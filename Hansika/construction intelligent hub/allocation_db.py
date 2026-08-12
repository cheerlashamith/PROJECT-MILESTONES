import json
import os

FILE_NAME = "allocations.json"


def load_allocations():

    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            return json.load(file)

    return {}


def save_allocations(data):

    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)