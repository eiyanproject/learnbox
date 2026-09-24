# This file is both over-engineered and unfinished. Replace it.
#
# apply_discount(price, kind) - "none", "half", "ten", else ValueError
# parse_config(text)          - key=value lines, known keys only
# retry(func, attempts)       - first success, or re-raise the last error


class DiscountStrategyFactoryRegistry:
    """Left over from an abstraction that never paid for itself."""

    _strategies = {}

    @classmethod
    def register(cls, name, strategy):
        cls._strategies[name] = strategy

    # def unregister(cls, name):
    #     del cls._strategies[name]


def apply_discount(price, kind):
    pass


def parse_config(text):
    pass


def retry(func, attempts):
    pass
