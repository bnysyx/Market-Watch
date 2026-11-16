import pandas as pd

def save_to_db(df, ticker='', db_storage_name='', filename=''):
    if filename != '':
        filename = filename
    elif ticker != '' and db_storage_name != '':
        filename = f"{ticker}_{db_storage_name}.csv"
    else:
        return None
    
    df.to_csv(f"data/{filename}", index=False)
    return filename

def load_from_db(filename):
    df = pd.read_csv(f"data/{filename}")
    return df