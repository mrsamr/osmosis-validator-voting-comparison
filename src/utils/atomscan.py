"""Data extraction functions"""


import requests
from collections import Counter


def get_validators() -> list:
    """Fetches a complete list of validators from Atomscan API"""
    
    URL = 'https://proxy.atomscan.com/osmo-lcd/cosmos/staking/v1beta1/validators'
    PAGE_SIZE = 1000
    
    r = requests.get(URL, params={'pagination.limit':PAGE_SIZE})
    validators = r.json()['validators']
    validators = [{'address':val['operator_address'],
                   'name':val['description']['moniker']}
                  for val in validators]
    
    duplicate_names = [x[0] for x in Counter([x['name'] for x in validators]).items() if x[1] > 1]
    
    validators = [{'address':val['address'],
                   'name':val['name'] if val['name'] not in duplicate_names
                                      else f"{val['name']} (...{val['address'][-6:]})"}
                  for val in validators]

    return validators
