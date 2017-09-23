import pandas as pd
import json

def _json_file_to_list(path):
    """Reads in a file containing (possibly) many json objects and puts them into a Python list"""
    with open(path) as f:
        data_list = f.readlines()
        json_strings = json.loads(json.dumps(data_list))
        result = [json.loads(json_string) for json_string in json_strings]
    return result

def _get_prices_and_runners(path):
    """Returns two lists of dicts, one containing prices and the other containing runner information.
    Doing these two tasks together avoids having to look through the json_list twice.
    Return value is given as a dictionary.
    """
    json_list = _json_file_to_list(path)
    prices = []
    runners = []
    for entry in json_list:
        mc = entry['mc'][0]
        try:
            runner_sublist = mc['marketDefinition']['runners']
            for runner in runner_sublist:
                runners.append(runner)
        except KeyError:
            pass    
        try:
            for item in mc['rc']:
                item['pt'] = entry['pt']
                prices.append(item)
        except KeyError:
            pass
        
    return {'prices':prices, 'runners':runners}

def _get_prices_df_long(path):
    """Returns dataframe with last-traded prices (expressed as probabilities) for all runners in long format"""
    prices_and_runners = _get_prices_and_runners(path)
    prices = prices_and_runners['prices']
    runners = prices_and_runners['runners']
    
    runner_ids_df = (pd.DataFrame.from_records(runners)
                     .drop_duplicates('id'))
    prices_df_long = (pd.DataFrame.from_records(prices)
                     .eval('last_traded_probability=1/ltp', inplace=False)
                     .assign(publish_time=lambda df: pd.to_datetime(df['pt'], unit='ms'))
                     .drop(['ltp', 'pt'], axis=1)
                     .merge(runner_ids[['id', 'name']], on='id')
                     .rename(columns={'id':'runner_id', 'name':'runner_name'})
                      [['publish_time', 'runner_id', 'runner_name', 'last_traded_probability']])
    return prices_df_long

def _get_prices_df_wide(path):
    """Returns dataframe with last-traded prices (expressed as probabilities) for all runners in wide format"""
    return (_get_prices_df_long(path)
            .pivot(index='publish_time', columns='runner_name', values='last_traded_probability')
            .ffill()) # we forward-fill because we're using last-traded probability

def get_prices(path, wide_format=True):
    """Reads Betfair market (not event) json file and 
    returns Pandas DataFrame of historical prices for all runners in wide (default) or long format.
    """
    if wide_format:
        return _get_prices_df_wide(path)
    else:
        return _get_prices_df_long(path)