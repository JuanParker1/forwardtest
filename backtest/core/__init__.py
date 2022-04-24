import pandas as pd
from backtest.core import settings

PRECISION = getattr(settings, "PRECISION", 8)

# init pandas settings
pd.options.display.precision=3
#pd.set_option('precision', PRECISION)
pd.set_option('display.float_format', lambda x: '%.{}f'.format(PRECISION) % x)
