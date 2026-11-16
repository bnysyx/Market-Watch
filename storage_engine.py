import pandas as pd

def save_to_db(df, ticker='', db_storage_name='', filename=''):
    if filename != '':
        output_filename = f"{filename}"
    elif ticker != '' and db_storage_name != '':
        output_filename = f"data/{ticker}_{db_storage_name}.csv"
    else:
        return None
    
    df.to_csv(f"{output_filename}", index=False)
    return output_filename

def load_from_db(filename):
    df = pd.read_csv(f"{filename}")
    return df