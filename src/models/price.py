class Price:
    """
    An instance of :class:`Price` holds a price and a currency.    

    Reference: https://github.com/siavashadpey/rebalance/blob/master/rebalance/cash/price.py
    """
    def __init__(self, price, currency="KRW"):
        """
        Initialization.
        Args:
            price (float): Price.
            currency (str, optional): Currency of price. Defaults to "KRW".
        """
        self._price = price
        self._currency = currency.upper()

    @property
    def price(self):
        """
        (float): Price (in own's currency).
        """
        return self._price

    @property
    def currency(self):
        """
        (str): Currency of price.
        """
        return self._currency

    def price_in(self, currency):
        """
        Converts price in specified currency.
        Args:
            currency (str): Currency in which to convert the price.
        Returns:
            (float): Price in specified currency.
        """
#         currency_exchange = Cash.currency_rates.get_rate(
#             self.currency, currency.upper())
        currency_exchange = 1

        return currency_exchange * self._price