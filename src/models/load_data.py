import pandas as pd

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Reference: https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class Balance:
   def __init__(self):
        self.access_path = '../../data/processed/'
        self.filename = 'balance_s.pkl'
        self.data = pd.read_pickle(self.access_path+self.filename)

@Singleton
class Instruments:
   def __init__(self):
        self.access_path = '../../data/processed/'
        self.filename = 'instruments_m.pkl'
        self.data = pd.read_pickle(self.access_path+self.filename)

@Singleton
class AdvisedPortfolios:
   def __init__(self):
        self.access_path = '../../data/processed/'
        self.filename = 'advised_portfolios.pkl'
        self.data = pd.read_pickle(self.access_path+self.filename)

@Singleton
class PriceDB:
   def __init__(self):
        self.access_path = '../../data/external/'
        self.filename = 'price_db_d.pkl'
        self.data = pd.read_pickle(self.access_path+self.filename)

