# -*- coding: utf-8 -*-
from .stock import Stock
#from strategy.strategy_ml import StrategyML
from strategy.strategy import Strategy 
from strategy.strategy_naive import StrategyNaive
from .wallet import Wallet
from ..utils.time_utils import *
# from ..utils.json_utils import *


class Bot:

    def __init__(self, stocks_id, date, initial_quantity, simulation_time, fixed_commission, prop_commission, moving_window, decrease_window, log, initial_account, lower, upper):
        self.quantity = initial_quantity
        self.stocks_id = stocks_id
        self.stocks = [Stock(name=stock_id, quantity=initial_quantity, date=date, simulation_time=simulation_time, fixed_commission=fixed_commission, prop_commission=prop_commission, moving_window=moving_window, decrease_window=decrease_window)
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
        print("Available cash : ", self.wallet.available_cash)
        print("Stocks amount : ", self.wallet.stocks_amount)
        return


    # def store_state(self, date):
    #     write_json("./src/data/wallet.JSON", {
    #         "virtual_account": self.wallet.virtual_account,
    #         "available_cash": self.wallet.available_cash,
    #         "stocks_amount": self.wallet.stocks_amount,
    #         "last_account": self.wallet.last_account,
    #         "total_commission": self.wallet.total_commission,
    #         "total_transaction": self.wallet.total_transaction,
    #         "storage_date": date
    #     })

    #     stock_content = {}
    #     for stock in self.stocks:
    #         stock_content[stock.getName()] = {
    #             "quantity": stock.getQuantity(),
    #             "cost_price": stock.getCostPrice(),
    #             "storage_date": date
    #         }

    #     write_json("./src/data/stock.JSON", stock_content)

    #     bot_content = {
    #         "initial_quantity": self.quantity,
    #         "stocks_id": self.stocks_id,
    #         "initial_account": self.initial_account,
    #         "last_account": self.last_account,
    #         "total_commission": self.total_commission,
    #         "total_transaction": self.total_transaction,
    #         "lower": self.lower,
    #         "upper": self.upper,
    #         "storage_date": date
    #     }

    #     write_json("./src/data/bot.JSON", bot_content)

    def run(self, date, strategy_name, log):
        """
        Run strategy and update wallet 
        """

        if log:
            print("\nOpen : \nWallet account : " + str(self.wallet.virtual_account)
                  + "\nStocks amount : " + str(self.wallet.stocks_amount) + "\nAvailable cash : "
                  + str(self.wallet.available_cash) + "\n")

        if self.stocks[0].getDateValue(date):
            if strategy_name == "naive":
                strategy = StrategyNaive(
                    self.stocks, date, self.initial_account, self.lower, self.upper)
            elif strategy_name == "ml":
                strategy = StrategyML(self.stocks, date, 3000)
            else:
                strategy = Strategy(self.stocks, date, 1000, 0.7, 0.3, self.wallet.available_cash)
            strats = strategy.run()

            self.wallet.save_last_account()

            for i, strat in enumerate(strats):
                # if the strategie says "buy" and the amount is available
                stock = self.stocks[i]
                if strat[0] == "buy" and strat[1] > 0 and self.wallet.buying_autorisation(i, strat[1], date):
                    stock.buy(int(strat[1]), self.wallet, stock.getDateValue(date))
                    if log:
                        print(
                            stock.getName() + " (" + str(stock.getQuantity()) + "|" +
                            str(stock.getDateValue(date)) + ")"
                            + " : Buy " + str(strat[1]) + " stock(s)" +
                            " -> +" + str(strat[1] * stock.getDateValue(date)) + " euros")

                # if the strategie says "sell"
                elif strat[0] == "sell" and stock.getQuantity() > 0 and strat[1] > 0:
                    sell = stock.sell(self.wallet, stock.getDateValue(date), quantity=int(strat[1]))
                    if sell is not None:
                        if log:
                            print(stock.getName() + " (" + str(stock.getQuantity()) + "|" +
                                  str(stock.getDateValue(date)) + ")" +
                                  " : Sell " + str(strat[1]) + " stock(s)" +
                                  " -> -" + str(strat[1] * stock.getDateValue(date)) + " euros")

                else:
                    if log:
                        print(stock.getName() + " (" + str(stock.getQuantity()) + "|" +
                              str(stock.getDateValue(date)) + ")" + " : No go")

            self.wallet.update(date)

            self.last_account = self.wallet.virtual_account
            self.total_commission = self.wallet.total_commission
            self.total_transaction = self.wallet.total_transaction

            if log:
                print("\nClose : \nWallet account : " + str(self.wallet.virtual_account)
                      + "\nStocks amount : " + str(self.wallet.stocks_amount) + "\nAvailable cash : "
                      + str(self.wallet.available_cash) + "\nVariation with previous day : "
                      + str(100*((self.wallet.virtual_account-self.wallet.last_account)/self.wallet.virtual_account)) + "\n")
        # else:
        #     print(date, " is not a trading day ! ")
