from bs4 import BeautifulSoup
import requests
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import urllib.request as ur
import pandas as pd

url = requests.get("https://finance.yahoo.com/lookup")
url.encoding = "utf-8"
soup = BeautifulSoup(url.text, "lxml", from_encoding = "gb18038")
l = []
for i in soup.find_all("tr"):
    l.append(i.text)
new_data = []
data = l[1:]
for i in data:
    print(i, len(i))
    lag = 0
    accumulator = 0
    previous = 0
    checker = 0
    if "LUNA" in i:
        left = i[0: 18]
        accumulator = 1
        right = i[18:]
        length = len(left)
    for p in range(len(i)):
        if accumulator == 0:
            print(i[p])
            try:
                print(int(i[p]))
                if previous == 1:
                    right = i[p:]
                    left = i[0:p]
                    print(p)
                    accumulator = 1
                    new_data.append(left)
                    length = len(left)
                    print(left)
                    print(right)
                    print(True)
            except:
                previous = 1
                continue
        if accumulator >= 1 and p >= length:
            previous = 0
            np = p - length
            try:
                int(right[np])
            except:
                previous = 1
            print(p, np)
            if right[np] == "+" or right[np] == "-" or right[np] == "%" and previous == 1:
                left = right[0:np].replace(",", '')
                length += len(left) + 1
                print(right[np], left)
                if lag == 0:
                    price_change = float(left)
                else:
                    price_change = -float(left)
                if right[np] == "-":
                    lag = 1
                right = right[np + 1:]
                new_data.append(price_change)

l = list(zip(*[iter(new_data)]*4))
print(l)
frame = pd.DataFrame(l)
frame.columns = ['SymbolName','LastPrice','Change','%Change']
frame.index = frame['SymbolName']
frame.drop(axis = 1, columns = 'SymbolName', inplace = True)
print(frame)