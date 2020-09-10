import numpy as np
import time


class Strategy:
    """
    This class will define the buy and sell strategy
    """

    def __init__(self, stocks, date, unit_price, sell_threshold, buy_threshold):
        self.__stocks = stocks
        self.__date = date
        self.__unit_price = unit_price
        self.__sell_threshold = sell_threshold
        self.__buy_threshold = buy_threshold

    def run(self):
        result = []
        for stock in self.__stocks:
            # Calculation of the RSI
            rsi = stock.getRSI(self.__date, 14)
            stock_price = stock.getDateValue(self.__date)
            normalized_rsi = rsi / 100
            stoch = stock.getStoch(self.__date, 14)
            normalized_stoch = stoch / 100
            score = np.mean([normalized_stoch, normalized_rsi])

            if self.__buy_threshold < score < self.__sell_threshold:
                result.append(["no go", np.nan])
            elif score < self.__buy_threshold:
                factor = (self.__buy_threshold - rsi) * 10
                amount = factor * self.__unit_price
                nb_stocks = int(amount // stock_price)
                if amount >= stock_price:
                    result.append(["buy", nb_stocks])
                else:
                    result.append(["no go", np.nan])
            else:
                factor = (rsi - self.__sell_threshold) * 10
                amount = factor * self.__unit_price
                nb_stocks = int(amount // stock_price)
                if amount >= stock_price:
                    result.append(["sell", nb_stocks])
                else:
                    result.append(["no go", nb_stocks])
        return result