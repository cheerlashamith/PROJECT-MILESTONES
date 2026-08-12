import pandas as pd

def create_data(cost, workers, months):

    data = {
        "Category":["Cost","Workers","Months"],
        "Value":[cost, workers, months]
    }

    return pd.DataFrame(data)