"""Data extraction functions from Flipside Crypto"""

import requests


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
