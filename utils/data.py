"""Data extraction and prep functions"""


import requests
import pandas as pd
import numpy as np
from itertools import permutations


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


def compile_voting_history(votes_df: pd.DataFrame, options: list) -> pd.DataFrame:
    """Prepares a table of votes per governance proposal for all selected validators.
    
    Parameters
    ----------
    votes_df : pd.DataFrame
        A table of votes per validator per proposal.
    
    options : list of dict
        The list of validators selected in-app for comparison.
    
    Returns
    -------
    voting_history_df : pd.DataFrame
        A side-by-side table of votes for all selected validators across a set of
        governance proposals.
    
    """
    
    # Names of selected validators
    selected_names = [x['name'] for x in options]
    
    # Validators that don't have any voting data yet
    missing_names = [n for n in selected_names if n not in votes_df['validator_name'].drop_duplicates().tolist()]
    
    # Filter voting data of selected validators only
    filtered_votes_df = votes_df.merge(pd.DataFrame(options), how='inner', left_on='validator_address', right_on='address')
    
    # Create side-by-side DataFrame
    voting_history_df = filtered_votes_df.pivot(index='proposal_id', columns='validator_name', values='vote')
    voting_history_df = voting_history_df.replace({'-':np.nan})
    
    # Create "blank" columns for validators without voting data
    for mn in missing_names: voting_history_df[mn] = np.nan
    
    return voting_history_df


def format_voting_history(voting_history_df: pd.DataFrame, proposals_df: pd.DataFrame, 
                          options: list, show_all_proposals: bool = False) -> pd.DataFrame:
    """Prepares a formatted DataFrame of validator voting history for display as an html table.
    
    Parameters
    ---------
    voting_history_df: pd.DataFrame
        A side-by-side table of votes for all selected validators across a set of
        governance proposals.
    
    proposals_df : pd.DataFrame
        A table of governance proposals (IDs and titles).
    
    options : list of dict
        The list of validators selected in-app for comparison.
    
    show_all_proposals: bool, default False
        True if all proposals, including those without votes from the selected
        validators, should be displayed in the output table.
    
    Returns
    -------
    formatted_df : pd.DataFrame
    
    """

    formatted_df = voting_history_df.copy()
    
    # Merge proposal titles
    formatted_df = formatted_df.merge(proposals_df, how='inner', left_index=True, right_on='id')
    
    # Format index and headers
    formatted_df['id'] = formatted_df['id'].astype('str').str.rjust(5)
    formatted_df = formatted_df.rename(columns={'id':'ID', 'title':'Proposal'})
    formatted_df = formatted_df.set_index(['ID','Proposal'])
    
    # Sort proposals from latest to oldest
    formatted_df = formatted_df.sort_index(ascending=False)
    
    # Order columns by selection order
    selected_names = [x['name'] for x in options]
    formatted_df = formatted_df[[v for v in selected_names if v in formatted_df.columns.tolist()]]
    
    # Truncate long validator names
    formatted_df.columns = [v.ljust(18) if len(v)<=18 else v[:15]+'...' for v in formatted_df.columns]
    
    # If toggled, hide proposals where none of the selected validators have voted on
    if show_all_proposals == False:
        formatted_df = formatted_df.loc[formatted_df.isnull().mean(axis=1) < 1.0]
        
    # Format blank cells
    formatted_df = formatted_df.fillna('-')

    return formatted_df


def create_similarity_matrix(options: list, voting_history_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates a voting similarity matrix for all pairs of validators among those selected.
    
    Parameters
    ----------
    options : list of dict
        The list of validators selected in-app for comparison.
    
    voting_history_df : pd.DataFrame
        A side-by-side table of votes for all selected validators across a set of
        governance proposals.
    
    Returns
    -------
    similarity_df : pd.DataFrame
        A dataframe of similarity scores between pairs of validators.
    
    """
    
    
    # List down all validator pairs
    selected_names = [x['name'] for x in options]
    pairs = list(permutations(selected_names, 2))
    similarity_scores = []

    for p in pairs:
        pair_votes = voting_history_df[[p[0],p[1]]]            
        num_proposals = pair_votes.shape[0]
        similarity = (pair_votes.iloc[:,0] == pair_votes.iloc[:,1]).mean()

        similarity_scores.append({'validator_0':p[0],
                                  'validator_1':p[1],
                                  'num_proposals':num_proposals,
                                  'similarity':similarity})

    similarity_df = pd.DataFrame(similarity_scores)
    similarity_df = similarity_df.pivot(index='validator_0', columns='validator_1', values='similarity')
    similarity_df = similarity_df.loc[selected_names, selected_names]
    similarity_df = similarity_df.fillna(0)
    similarity_df.columns.name = 'Validator A'
    similarity_df.index.name = 'Validator B'

    n = similarity_df.shape[0]
    for idx in range(n):
        similarity_df.iloc[idx,idx] = 1
        similarity_df.iloc[:idx,idx] = None

    similarity_df = (similarity_df * 100).round(2)
    
    return similarity_df