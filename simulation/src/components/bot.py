from .stock import Stock
from strategy.strategy import Strategy
from strategy.strategy_naive import StrategyNaive
from .wallet import Wallet
from ..utils.time_utils import *


class Bot:

    def __init__(self, stocks_id, date, simulation_time, fixed_commission, prop_commission, moving_window, decrease_window, log, initial_account, lower, upper):
        self.quantity = 1
        self.stocks_id = stocks_id
        self.stocks = [Stock(name=stock_id, quantity=1, date=date, simulation_time=simulation_time, fixed_commission=fixed_commission, prop_commission=prop_commission, moving_window=moving_window, decrease_window=decrease_window)
                       for stock_id in self.stocks_id]
        self.wallet = Wallet(self.stocks, initial_account)
        self.initial_account = initial_account
        self.last_account = initial_account
        self.total_commission = 0
        self.total_transaction = 0
        self.lower = lower
        self.upper = upper

    def stock_state(self, date):
        for stock in self.stocks:
            print(stock.show(date))
        print("Available cash", self.wallet.available_cash)
        print("Stocks amount", self.wallet.stocks_amount)
        return

    def run(self, date, strategy_name, log):
        """
        Run strategy and update wallet 
        """

        if self.stocks[0].getDateValue(date):
            if strategy_name == "naive":
                strategy = StrategyNaive(
                    self.stocks, date, self.initial_account, self.lower, self.upper)
            else:
                strategy = Strategy(self.stocks, date, 1000, 0.7, 0.3)
            strats = strategy.run()

            self.wallet.save_last_account()

            for i, strat in enumerate(strats):
                # if the strategie says "buy" and the amount is available
                if strat[0] == "buy" and strat[1] > 0 and self.wallet.buying_autorisation(i, strat[1], date):
                    if log:
                        print(
                            "Buy " + str(strat[1]) + " stock(s) of " + self.stocks[i].getName())
                    self.wallet.buy(i, date, int(strat[1]))
                    self.stocks[i].buy(
                        int(strat[1]), self.stocks[i].getDateValue(date))

                # if the strategie says "sell"
                elif strat[0] == "sell" and self.stocks[i].getQuantity() > 0 and strat[1] > 0:

                    sell = self.stocks[i].sell(int(strat[1]))
                    if sell is not None:
                        self.wallet.sell(i, date)
                        if log:
                            print(
                                "Sell " + str(self.stocks[i].getQuantity()) + " stock(s) of " + self.stocks[i].getName())

                else:
                    if log:
                        print("No go")

            self.wallet.update(date)

            self.last_account = self.wallet.virtual_account
            self.total_commission = self.wallet.total_commission
            self.total_transaction = self.wallet.total_transaction

            if log:
                print("Date : ", date, "Wallet account : ", self.wallet.virtual_account, ", Stocks amount : ", self.wallet.stocks_amount, ", Available cash : ", self.wallet.available_cash, "\nVariation with previous day : ",
                      int(10000*(self.wallet.virtual_account-self.wallet.last_account)/self.wallet.virtual_account)/100)
        # else:
        #     print(date, " is not a trading day ! ")
