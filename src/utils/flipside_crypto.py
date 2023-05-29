"""Data extraction functions from Flipside Crypto"""

import requests
import os
import pandas as pd
from flipside import Flipside


FLIPSIDE_API_KEY = os.environ.get('FLIPSIDE_API_KEY')


def get_validators_from_api() -> list:
    """Fetches a complete list of validators."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/cdf4d7a8-bb09-4e0b-ba70-1bd663b2e0ae/data/latest'
    r = requests.get(URL)
    validators = [{'address':val.get('VALIDATOR_ADDRESS'),
                   'name':val.get('VALIDATOR_NAME'),
                   'voting_power':val.get('VOTING_POWER')}
                  for val in r.json()]
    return validators


def get_proposals_from_api() -> dict:
    """Fetches complete list of governance proposals."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/eab92e49-bb27-460b-9c3f-74f9cd9db34f/data/latest'
    r = requests.get(URL)
    proposals = [{'id':val.get('PROPOSAL_ID'),
                  'title':val.get('PROPOSAL_TITLE')}
                  for val in r.json()]
    return proposals


def get_validator_votes_from_api() -> list:
    """Extracts complete list of votes for all validators."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/c956f149-348a-4939-8ff8-500924da7e6e/data/latest'
    r = requests.get(URL)
    votes = r.json()
    votes = [{'validator_address':val.get('VALIDATOR_ADDRESS'),
              'proposal_id':int(pid),
              'vote':vote} for val in votes for pid,vote in val.get('VOTES').items()]
    return votes


def query(stmt: str, api_key: str = FLIPSIDE_API_KEY, return_df: bool = True) -> list:
    """Executes a query on Flipside and retrieves the result.
    
    Parameters
    ----------
    stmt : str
        The SQL statement.
        
    Returns
    -------
    result : list or pd.DataFrame
        A list of records (or DataFrame) of the query results.
    
    """
    
    assert api_key is not None, 'Please provide an API key.'
    
    # Initialize Flipside client
    flipside = Flipside(api_key, 'https://api-v2.flipsidecrypto.xyz')
    
    # Run the query against Flipside's query engine and await the results
    query_result_set = flipside.query(stmt)
    result = query_result_set.records
    
    if return_df:
        result = pd.DataFrame(result).set_index('__row_index')
    
    return result