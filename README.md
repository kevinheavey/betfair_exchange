# betfair_exchange
Collection of scripts related to the Betfair Exchange and its historical data

Currently this repository contains read_historical.py, which can be used to read Betfair historical data from Betfair market format files using the get_prices function, which returns a Pandas DataFrame in wide or long format

```python
from read_historical import get_prices
df = get_prices(filepath)
```
