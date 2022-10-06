import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dateutil
from datetime import datetime, timedelta
from pandas_datareader import data as pdr


profit_express = pd.read_csv("AShareProfitExpresscopy.csv", index_col = "S_INFO_WINDCODE",parse_dates = ["ANN_DT"],error_bad_lines = False)

profit_table = pd.DataFrame()
for i in range(len(profit_express.index)):
    series = pd.Series({"ANN_DT":profit_express.iloc[i, 0], "net_profit":profit_express.iloc[i, 1], "EPS":profit_express.iloc[i, 2], "YO":profit_express.iloc[i, 3]},name = profit_express.index[i])
    profit_table = profit_table.append(series)


def equity_selection_profit(year, season, iteration):
    selected_stocks = pd.Series()
    for i in profit_table.index:
        if i in selected_stocks.index:
            continue
        else:
            pivot = 0
            new_df = profit_table.loc[i]
            try:
                new_df.index = new_df["ANN_DT"]
            except:
                continue
            for time in new_df.index:
                if datetime(year - iteration, season * 3 - 2, 1) < time < datetime(year - iteration, season * 3, 31):
                    if new_df.loc[time].net_profit < 3000000:
                        break
                    else:
                        each = iteration
                        stop = 0
                        increase_speed = []
                        for each_iteration in range(iteration):
                            accumulate = 0
                            last_year = time
                            each -= 1
                            if stop == 1:
                                break
                            for t in new_df.index:
                                if datetime(year - each, season * 3 - 2, 1) < t < datetime(year - each, season * 3, 31):
                                    increase = ((new_df.loc[t].net_profit - new_df.loc[last_year].net_profit) /
                                                new_df.loc[last_year].net_profit)
                                    if increase > 0:
                                        increase_speed.append(increase)
                                        last_year = t
                                        if each == 0:
                                            transaction_time = t
                                    else:
                                        stop = 1
                                        break
                                else:
                                    accumulate += 1
                            if accumulate == len(new_df.index):
                                stop = 1
                        if len(increase_speed) == iteration:
                            pivot = 1
                            temp = []
                            while len(increase_speed) != 1:
                                for speed_id in range(len(increase_speed)):
                                    try:
                                        double = (increase_speed[speed_id + 1] - increase_speed[speed_id]) / \
                                                 increase_speed[speed_id]
                                        if double > 0:
                                            temp.append((increase_speed[speed_id + 1] - increase_speed[speed_id]) /
                                                        increase_speed[speed_id])
                                        else:
                                            temp.append(0)
                                    except:
                                        break
                                increase_speed = temp.copy()
                                temp = []
                            stock = pd.Series(
                                {i: [increase_speed[0], new_df.loc[transaction_time].EPS, transaction_time]})

            if pivot == 0:
                continue
            else:
                selected_stocks = selected_stocks.append(stock)
                continue

    selected_stocks = selected_stocks.sort_values(ascending=False)
    return (selected_stocks)

def equity_selection_valuation(year,season,iteration):
    final_selection = equity_selection_profit(year, season, iteration)
    for i in final_selection.index:
        print(i)
        try:
            price_range = pdr.DataReader(i, "yahoo", datetime(year, season * 3 - 2, 1), datetime(year, season * 3, 31))["Adj Close"]
            price = price_range.mean()
            pe = price / final_selection[i][1]
            if pe >= 50:
                final_selecion.drop(index=i, inplace=True)
            else:
                loop_indicator = 1
                purchase_time = final_selection[i][2]
                while loop_indicator == 1:
                    try:
                        purchase_price = price_range[purchase_time]
                        loop_indicator = 0
                    except:
                        purchase_time = purchase_time + timedelta(days=+1)
                        continue
                final_selection[i].append(purchase_price)

        except:
            final_selection.drop(index=i, inplace=True)
    if len(final_selection) > 25:
        return final_selection[0:25]
    else:
        return final_selection


def trade(portfolio, cost, stock, time, sell_or_buy):
    loop_indicator = 1
    while loop_indicator == 1:
        try:
            current_price = pdr.DataReader(stock.index[0], "yahoo", time, time + timedelta(days=+7))["Adj Close"][time]
            loop_indicator = 0
        except:
            time = time + timedelta(days=+1)
            continue
    loop_indicator = 1

    if sell_or_buy == "sell":
        cost -= current_price
        portfolio.drop(index=stock.index[0], inplace=True)
        new_portfolio = portfolio
    elif sell_or_buy == "buy":
        new_portfolio = portfolio.append(stock)
        cost += current_price
    return [cost, new_portfolio]


def calculate_cost(portfolio):
    total_worth = 0
    for i in portfolio.index:
        total_worth = total_worth + portfolio[i][3]
    return total_worth


def calculate_return(portfolio, cost, date_of_calculation):
    total_worth = 0
    for i in portfolio.index:
        price = pdr.DataReader(i, "yahoo", date_of_calculation + timedelta(days=-5), date_of_calculation + timedelta(days=+4))[
            "Adj Close"].mean()
        total_worth = total_worth + price
    return (total_worth - cost) / cost


def main(year, season, iteration, start_time):
    return_list = []
    index_list = []
    time_list = []
    time = start_time
    indicator = 0
    accumulator = 0
    while accumulator < iteration:
        if indicator == 0:
            new_selected = equity_selection_valuation(year, season, 2)
            print("step one completed")
            print("enter initial transaction")
            selected = new_selected
            cost = calculate_cost(selected)
            previous_index = pdr.DataReader("000001.SS", "yahoo", time + timedelta(days=-5), time + timedelta(days=+4))[
                "Adj Close"].mean()
            print("first index calculate")
            accumulator += 1
        else:
            if time.month in [1, 4, 7, 10]:
                new_selected = equity_selection_valuation(year, season, 2)
                print("step one completed")
                if season < 4:
                    season += 1
                else:
                    year += 1
                    season = 1
                for index in new_selected.index:
                    print("another transaction")
                    if index not in selected.index:
                        outcome = trade(selected, cost, new_selected[index:index], time, "buy")
                        cost = outcome[0]
                        selected = outcome[1]
                for index in selected.index:
                    if index not in new_selected.index:
                        outcome = trade(selected, cost, selected[index:index], time, "sell")
                        cost = outcome[0]
                        selected = outcome[1]
                accumulator += 1
            time_list.append(time)
            print("calculating return list ne")
            return_list.append(calculate_return(selected, cost, time))
            print("calculating current index")
            current_index = pdr.DataReader("000001.SS", "yahoo", time + timedelta(days=-5), time + timedelta(days=+4))["Adj Close"].mean()
            index_list.append((current_index - previous_index) / previous_index)
            previous_index = current_index
        indicator = 1
        time = time + timedelta(days=+ 31)
    plt.plot(time_list, return_list, lable = "portfolio return")
    plt.plot(time_list, index_list, label = "index return")
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Return")
    plt.show()



print(equity_selection_profit(2016, 1, 1))
