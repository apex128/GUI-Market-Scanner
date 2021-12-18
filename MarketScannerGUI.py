import numpy as np
import pandas as pd
import pandas_ta as ta
import os
from tqdm import tqdm
import yfinance as yf
import plotly.graph_objs as go
from numerize import numerize
import tkinter as tk

def displayChart(ticker, name, marketCap, folderName, timeframe, period, filterUpBars, filterDownBars, consec,
                 aboveEMA, belowEMA):
    # Download the data
    data = yf.download(tickers=ticker, period=period, interval=timeframe, progress=False)
    
    # Create the 21 ema
    moving_averages = ta.Strategy(
        name="moving indicators",
        ta=[
            {"kind": "ema", "length": 21},
        ]
    )
    
    # Disable multiprocessing, calculate averages
    data.ta.cores = 0  # optional, but requires if __name__ == "__main__" syntax if not set to 0
    data.ta.strategy(moving_averages)
    
    # Declare figure
    layout=go.Layout(
        autosize=False,
        width=1920,
        height=1080
    )
    fig = go.Figure(layout=layout)
    
    # Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                    open =data['Open'],
                    high =data['High'],
                    low  =data['Low'],
                    close=data['Close'], name = 'market data',
                    showlegend=False,
                    increasing_line_color='limegreen', increasing_fillcolor='limegreen',
                    decreasing_line_color='red',   decreasing_fillcolor='red'))
    
    # Add titles
    titleString = 'Ticker: ' + ticker + '; Company Name: ' + name + '; Timeframe: ' + timeframe
    titleString += '; Period: ' + period + '; Market Cap: ' + str(marketCap)
    fig.update_layout(
        title = titleString,
        yaxis_title='USD')
    
    # X-Axes
    fig.update_xaxes(
        rangeslider_visible=False
    )
    
    # Add the 21 EMA to the chart
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['EMA_21'],
            line=dict(color='#3399ff', width=1.5),
            name='21 EMA',
            showlegend=False
        )
    )
    
    Open =np.round(data['Open'], 2)
    High =np.round(data['High'], 2)
    Low  =np.round(data['Low'] , 2)
    Close=np.round(data['Close'],2)
    
    priceAboveEMA=False    
    if aboveEMA:
        # if price is above the 21 EMA
        if (Close[-1] > data['EMA_21'][-1]):
            priceAboveEMA=True
    
    priceBelowEMA=False
    if belowEMA:
        # if price is below the 21 EMA
        if (Close[-1] < data['EMA_21'][-1]):
            priceBelowEMA=True
    
    # Find 3 green candles in a row
    isConsec = True
    if filterUpBars:
        for i in range(-consec, 0):
            if (Close[i] <= Open[i]):
                isConsec = False
    
    # Find 3 red candles in a row
    if filterDownBars:
        for i in range(-consec, 0):
            if (Close[i] >= Open[i]):
                isConsec = False
    
    # Write to a file if conditions are met
    wrote = False
    if (isConsec):
        if (aboveEMA==priceAboveEMA and belowEMA==priceBelowEMA):
            fig.write_image(folderName + "/" + ticker + ".jpeg", engine="kaleido")
            wrote = True
    return wrote

def scan(minMarketCap, minVolume, sector, filterUpBars, filterDownBars, consec, aboveEMA, belowEMA, timeframe, period):
    print("Scanning for stocks with min market cap", numerize.numerize(minMarketCap), ", minVolume", numerize.numerize(minVolume), ".")
    print("Timeframe:", timeframe, ", period:", period)
    #tickersList=['ENTA', 'MPLN', 'PKI', 'IBB']
    # Downloaded from https://www.nasdaq.com/market-activity/stocks/screener
    tickers=pd.read_csv('nasdaq_list.csv')
    tickersFrame=pd.DataFrame(tickers, columns=['Symbol', 'Name', 'Market Cap', 'Sector', 'Volume'])
    # Remove stocks with a market cap of 0
    tickersFrame=tickersFrame.loc[tickersFrame['Market Cap'] != 0]
    # Remove stocks with no specified market cap
    tickersFrame['Market Cap'].replace('', np.nan, inplace=True)
    tickersFrame.dropna(subset=['Market Cap'], inplace=True)
    # Sort the dataframe by market cap in descending order
    tickersFrame=tickersFrame.sort_values('Market Cap', ascending=False)
    # Filter for stocks with a market cap greater than specified minimum
    tickersFrame=tickersFrame.loc[tickersFrame['Market Cap'] > minMarketCap]
    # Filter for stocks with volume > specified minimum
    tickersFrame=tickersFrame.loc[tickersFrame['Volume'] > minVolume]
    # Filter for stocks which are in the specified sector
    if (sector):
        print("Sector:", sector)
        tickersFrame=tickersFrame.loc[tickersFrame['Sector'] == sector]
    print()
    print(len(tickersFrame), "stocks met initial criteria:")
    print(', '.join(tickersFrame['Symbol'].values))
    print("\nScan parameters:")
    if (aboveEMA):
        print("Price must be above 21 EMA.")
    if (belowEMA):
        print("Price must be below 21 EMA.")
    if (filterUpBars):
        print("Must have " + str(consec) + " green candles in a row.")
    if (filterDownBars):
        print("Must have " + str(consec) + " red candles in a row.")
    print("\nScanning...")
    
    tickersList=tickersFrame['Symbol'].values
    
    i = 0
    while os.path.exists("result%s" % i):
        i += 1
    os.mkdir("result%s" % i)
    folderName="result%s" % i
    
    # Create charts for each stock
    count = 0
    for ticker in tqdm(tickersList):
        try:
            name=tickersFrame[tickersFrame['Symbol'] == ticker]['Name'].values[0]
            marketCap=int(tickersFrame[tickersFrame['Symbol'] == ticker]['Market Cap'].values[0])
            if (displayChart(ticker, name, numerize.numerize(marketCap), folderName, timeframe, period, filterUpBars, filterDownBars, consec,
                             aboveEMA, belowEMA)):
                count += 1
        except:
            pass
    
    print("\nAll charts processed.")
    return count

def runScanner():
    numResults = scan(int(marketCapText.get("1.0", tk.END)),
                      int(volumeText.get("1.0", tk.END)),
                      selectedSector.get().strip(),
                      filterUpBars.get(), filterDownBars.get(), int(consecText.get("1.0", tk.END)),
                      aboveEMA.get(), belowEMA.get(),
                      timeframeText.get("1.0", tk.END).strip(), periodText.get("1.0", tk.END).strip())
    print(numResults, "results found.\n\n")

window = tk.Tk()
width = 300
height = 500
window.geometry(str(width) + "x" + str(height))
window.minsize(width, height)
window.maxsize(width, height)
window.title("Market Scanner")

tk.Label(window, text = "Interval:").pack(side="top")
timeframeText = tk.Text(master=window, height=1, width=15)
timeframeText.insert(tk.END, "1d")
timeframeText.pack(side="top")

tk.Label(window, text = "Period:").pack(side="top")
periodText = tk.Text(master=window, height=1, width=15)
periodText.insert(tk.END, "250d")
periodText.pack(side="top")

tk.Label(window, text = "Min. Market Cap:").pack(side="top")
marketCapText = tk.Text(master=window, height=1, width=15)
marketCapText.insert(tk.END, "100000000000")
marketCapText.pack(side="top")

tk.Label(window, text = "Min. Volume:").pack(side="top")
volumeText = tk.Text(master=window, height=1, width=15)
volumeText.insert(tk.END, "5000000")
volumeText.pack(side="top")

filterUpBars = tk.IntVar()
tk.Checkbutton(window, text="Consec up bars", variable=filterUpBars).pack()
filterDownBars = tk.IntVar()
tk.Checkbutton(window, text="Consec down bars", variable=filterDownBars).pack()

tk.Label(window, text = "Number of consec bars (if selected):").pack(side="top")
consecText = tk.Text(master=window, height=1, width=15)
consecText.insert(tk.END, "3")
consecText.pack(side="top")

aboveEMA = tk.IntVar()
tk.Checkbutton(window, text="Above 21 EMA?", variable=aboveEMA).pack()
belowEMA = tk.IntVar()
tk.Checkbutton(window, text="Below 21 EMA?", variable=belowEMA).pack()

SECTORS = [
'',
'Health Care',
'Consumer Services',
'Finance',
'Miscellaneous',
'Capital Goods',
'Transportation',
'Technology',
'Consumer Durables',
'Consumer Non-Durables',
'Public Utilities',
'Basic Industries',
'Energy'
]
tk.Label(window, text = "Sector:").pack(side="top")
selectedSector = tk.StringVar(window)
selectedSector.set(SECTORS[0]) # default value
w = tk.OptionMenu(window, selectedSector, *SECTORS)
w.pack()

scanButton = tk.Button(text="Scan", command=runScanner)
scanButton.pack(side="top")

window.mainloop()
