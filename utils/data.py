"""Data extraction functions"""


import requests
import pandas as pd


def get_validators() -> list:
    """Fetches a complete list of validators."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/cdf4d7a8-bb09-4e0b-ba70-1bd663b2e0ae/data/latest'
    r = requests.get(URL)
    validators = [{'address':val.get('VALIDATOR_ADDRESS'),
                   'name':val.get('VALIDATOR_NAME'),
                   'voting_power':val.get('VOTING_POWER')}
                  for val in r.json()]
    
    return validators


def get_proposals() -> dict:
    """Fetches complete list of governance proposals."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/eab92e49-bb27-460b-9c3f-74f9cd9db34f/data/latest'
    r = requests.get(URL)
    proposals = [{'id':val.get('PROPOSAL_ID'),
                  'title':val.get('PROPOSAL_TITLE')}
                  for val in r.json()]
    return proposals


def get_validator_votes() -> list:
    """Extracts complete list of votes for all validators."""
    
    URL = 'https://api.flipsidecrypto.com/api/v2/queries/c956f149-348a-4939-8ff8-500924da7e6e/data/latest'
    r = requests.get(URL)
    votes = r.json()
    votes = [{'validator_address':val.get('VALIDATOR_ADDRESS'),
              'proposal_id':int(pid),
              'vote':vote} for val in votes for pid,vote in val.get('VOTES').items()]
    return votes


def prepare_complete_votes_df(validators, proposals, votes) -> pd.DataFrame:
    """Merges and formats raw datasets."""
    
    validators_df = pd.DataFrame(validators)
    proposals_df = pd.DataFrame(proposals)
    votes_df = pd.DataFrame(votes)
    
    complete_votes_df = votes_df.copy()
    complete_votes_df = complete_votes_df.merge(validators_df, how='left', left_on='validator_address', right_on='address')
    complete_votes_df = complete_votes_df.rename(columns={'name':'validator_name'})
    complete_votes_df = complete_votes_df.merge(proposals_df, how='left', left_on='proposal_id', right_on='id')
    complete_votes_df = complete_votes_df.rename(columns={'title':'proposal_title'})
    complete_votes_df = complete_votes_df[['validator_address','validator_name',
                                           'proposal_id','proposal_title','vote']]
    
    return complete_votes_df


def fetch_datasets() -> dict:
    """Returns a set of DataFrames to be used in the Streamlit app."""
    
    validators = get_validators()
    proposals = get_proposals()
    votes = get_validator_votes()
    
    proposals_df = pd.DataFrame(proposals)
    complete_votes_df = prepare_complete_votes_df(validators, proposals, votes)
    
    return {'validators':validators,
            'proposals_df':proposals_df,
            'votes_df':complete_votes_df}

