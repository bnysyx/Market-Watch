import os
from dotenv import load_dotenv
from datetime import date

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain.agents import create_agent

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# internal engine
from storage_engine import load_from_db, save_to_db


os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(temperature=0, model_name="openai/gpt-oss-20b", api_key=groq_key)

# Yahoo News Kit
yahoo_tool = YahooFinanceNewsTool()


@tool
def load_stock_data(ticker:str, start_date:str, end_date:str):
    """
    Action: Loads times-series stock data and stores data locally.
    Trigger: Use this whenever the user asks for an overview, tabular data or time-related developments and statistics.
    Prerequisites: None
    Inputs: ticker (string) as officially acknoledged by Yahoo Finance. start_date (string), end_date (string) are to be provided in the format: YYYY-MM-DD.
    """
    file_identifier = 'data'
    df = yf.download(ticker, start=start_date, end=end_date)
    df.columns = df.columns.droplevel(1)
    df = df.reset_index()   
    df.rename(columns={'Close':'price','Date': 'date'}, inplace=True)

    column_list = df.columns.to_list()
    dtype_list = df.dtypes.to_list()

    df_info = dict(zip(column_list, dtype_list))
    
    if df.empty:
        return {"status": 'Failed to download and create dataframe. Provide correct ticker symbol and start/end date.'}
    else:    
        output_filename = save_to_db(df, ticker, "data")
        return {
            'status': f'Dataframe has been successfully created for {start_date} to {end_date} of {ticker} and saved locally', 
            'filename':output_filename,
            'dataframe_info':df_info
            }


@tool
def calc_moving_average(filename:str, day_count:int):
    """
    Action: Create a moving average on the stored dataset.
    Trigger: You MUST use this tool whenever the user asks for a moving average.
    Prerequisites: You must run 'load_stock_data' first to download the data and get the correct filename. 
    Inputs: filename (string) and day_count(integer) as a determinant of the moving average's observation period.
    """
    df = load_from_db(filename)
    df[f'SMA_{day_count}'] = df['price'].rolling(window=day_count).mean()

    column_list = df.columns.to_list()
    dtype_list = df.dtypes.to_list()

    df_info = dict(zip(column_list, dtype_list))

    if df.empty:
        return {"status": 'Failed to load dataframe. Provide correct filename / data.'}
    elif f'SMA_{day_count}' not in df.columns:
        return {"status": 'Failed to create moving average. Provide valid data / day count'}
    else:    
        output_filename = save_to_db(df, filename=filename)
        if output_filename is not None:
            return {
                'status': 'Moving Average has been successfully created and database updated.', 
                'filename':output_filename,
                'dataframe_info':df_info,
                }

@tool
def create_bull_indicator(filename: str, day_count:int):
    """
    Action: Create an indicator for a bull market in terms of closing price > moving average = 1, 0 otherwise on the stored dataset.
    Trigger: You MUST use this tool whenever the user asks for market indication based on technical analysis.
    Prerequisites: You must run 'calc_moving_average' first to receive the correct moving average information. 
    Inputs: filename (string) and day_count(integer) as a determinant of the moving average's observation period (as previously used).
    """
    

    df = load_from_db(filename)
    df['bull_indicator'] = (df['price'] > df[f'SMA_{day_count}']).astype(int)

    column_list = df.columns.to_list()
    dtype_list = df.dtypes.to_list()

    df_info = dict(zip(column_list, dtype_list))

    if df.empty:
        return {"status": 'Failed to load dataframe. Provide correct filename / data.'}
    elif 'bull_indicator' not in df.columns:
        return {"status": 'Failed to create bull indicator. Provide valid data / day count'}
    else:    
        output_filename = save_to_db(df, filename=filename)
        if output_filename is not None:
            return {
                'status': 'Bull indicator has been successfully created and database updated', 
                'filename':output_filename,
                'dataframe_info': df_info,
                }

@tool
def load_stock_info(ticker:str):
    """
    Action: Loads general stock and company information.
    Trigger: Use this whenever the user asks for an overview, dossier, or general company statistics
    Prerequisites: None
    Inputs: ticker (string) as officially acknoledged by Yahoo Finance
    """
    ticker_data = yf.Ticker(ticker)
    df = pd.DataFrame([ticker_data.info])

    column_list = df.columns.to_list()
    dtype_list = df.dtypes.astype(str).to_list()

    df_info = dict(zip(column_list, dtype_list))

    if df.empty:
        return {"status": 'Failed to download and create dataframe. Provide correct ticker symbol and start/end date.'}
    else:
        output_filename = save_to_db(df, ticker, "ticker_info")
        if filename is not None:
            return {
                        'status': f'Dataframe for {ticker} successfully created and saved locally', 
                        'filename':output_filename,
                        'dataframe_info':df_info
                    }

@tool
def read_stock_info(filename: str, selected_columns: list):
    """
    Action: Loads locally saved stock information and provides specifically selected information.
    Trigger: You MUST use this tool whenever you need descriptive or general information of a stock or company.
    Prerequisites: You must run 'load_stock_info' first to download the data and get the correct filename and columns to select.
    Inputs: filename (string) and selected_columns (list). Any column name MUST strictly be contained in 'dataframe_info'.
    """

    df = load_from_db(filename)
    df = df[selected_columns]
    ticker_info_dict = df.to_dict(orient="records")


    if df.empty:
        return {"status": 'Failed to select data fields. Provide correct field name.'}
    else:
        return {
                'status': f'Data from {filename} successfully loaded and sliced', 
                'data':ticker_info_dict,
            }

@tool
def read_tabular_data(filename: str, number_of_entries: int =10):
    """
    Action: Loads locally saved stock data and provides time-series data for a specific number of selected last data entries (default = 10).
    Trigger: You MUST use this tool whenever you need historic data in a tabular way or if you attempt to create any markdown table. 
    Prerequisites: You must at least run 'load_stock_data' first to download the data and get the correct filename.
    Inputs: filename (string) and number_of_entries (integer) (optional).
    """
    df = load_from_db(filename)
    df_dict = df.tail(number_of_entries).to_dict(orient='records')

    if df.empty:
        return {"status": 'Failed to select data rows. Provide correct field name.'}
    else:
        return {
                'status': f'Data from {filename} successfully loaded and sliced', 
                'data':df_dict,
            }


@tool
def plot_graph(filename: str, ticker:str, day_count:int):
    """
    Action: Creates a visual plot of the stock price and moving average.
    Trigger: You MUST use this tool whenever the user asks for a 'plot', 'chart', 'graph', or 'graphical representation'.
    Prerequisites: You must run `calc_moving_average` first to get the correct filename.
    Inputs: filename (string), ticker (string), and day_count (integer).
    """

    df = load_from_db(filename)
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(df.index, df['price'], label='Close Price', color='#1f77b4', linewidth=1.5)

    ax.plot(df.index, df[f'SMA_{day_count}'], label=f'{day_count}-day SMA', color='#ff7f0e', linestyle='--')

    # Format plot
    ax.set_title('Stock Price with Moving Averages', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend(loc='upper left')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    output_filename = f'data/{ticker}_chart.png'
    plt.savefig(output_filename)

    return {
        'status': 'Graph has been successfully plotted and saved locally', 
        'filename':output_filename,
        }

def ai_agent(chat_history):
    tools = [yahoo_tool, load_stock_data, load_stock_info, calc_moving_average, create_bull_indicator, plot_graph, read_stock_info]

    agent = create_agent(model=llm, tools=tools)



    response = agent.invoke({"messages":chat_history})
    return response


def initialize_agent():
    today = date.today()
    chat_history= [(
        "system",f"""
                Persona: You provide helpful insights into stock developments and current market movements. Choose the information based on the user-oriented depth and complexity.

                Output format: 
                (1) Provide the output in a markdown schema as follows:
                '##' for 'Title / Header' 
                '####' for 'Subtitle / Subheader'
                '**' for 'key highlights'
                ![Title](filename) for local source png files
                '-' for a list of unordered elements
                '1,2,3' for a list of ordered elements
                'Table Syntax' for tabular data / information

                (2) Depending on the depth of the prompt use the following output strucures as baseline:
                a) short --> general company summary, include up to 3 financial key information, include last price
                b) mid -->  short news summary, general company summary, include up to 7 financial key information
                c) long --> detailed news summary, detailed company summary, include up to 20 financial key information

                Audience: The user can range from a financial analyst to an amateur. 

                Methods: You are given different tools in order to address the users need and provide information in different ways. 

                - You are explicitly forbidden to estimate or making up any financial numbers in your analysis or output.
                - For reference: Today's date is {today}
                """)]
    return chat_history

if __name__ == "__main__":
    prompt = "Download Apple stock data for the last year, calculate the 30-day moving average, and create a graphical display of the price."
    
    chat_history = initialize_agent()
    chat_history.append(("user",prompt))
    response = ai_agent(chat_history)
    
    print("AI",response["messages"][-1].content)

    for line in response["messages"]:
        line.pretty_print()