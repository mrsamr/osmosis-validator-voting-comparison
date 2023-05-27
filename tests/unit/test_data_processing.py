import pytest
import pandas as pd
from utils.data import prepare_complete_votes_df
from utils.data import compile_voting_history
from utils.data import format_voting_history
from utils.data import create_similarity_matrix


@pytest.fixture
def validators():
    return pd.read_csv('tests/_test_data/validators.csv').to_dict(orient='records')

@pytest.fixture
def proposals():
    return pd.read_csv('tests/_test_data/proposals.csv').to_dict(orient='records')

@pytest.fixture
def votes():
    return pd.read_csv('tests/_test_data/votes.csv').to_dict(orient='records')

@pytest.fixture
def valid_votes():
    return ['YES','NO','NO WITH VETO','ABSTAIN']

@pytest.fixture
def complete_votes_df(validators, proposals, votes):
    return prepare_complete_votes_df(validators, proposals, votes)

@pytest.fixture
def proposals_df(proposals):
    return pd.DataFrame(proposals)

@pytest.fixture
def validator_selection(validators):
    return validators[:5]

@pytest.fixture
def voting_history_df(complete_votes_df, proposals_df, validator_selection):
    return compile_voting_history(complete_votes_df, proposals_df, validator_selection)

@pytest.fixture
def formatted_voting_history_df(voting_history_df, validator_selection):
    return format_voting_history(voting_history_df, validator_selection)

@pytest.fixture
def similarity_df(validator_selection, voting_history_df):
    return create_similarity_matrix(validator_selection, voting_history_df)


def test__complete_votes__row_count(votes, complete_votes_df):
    assert len(votes) == complete_votes_df.shape[0]
    
def test__complete_votes__columns_list(complete_votes_df):
    COLUMNS = ['validator_address','validator_name','proposal_id','proposal_title','vote']
    assert set(complete_votes_df.columns) == set(COLUMNS)
    
def test__complete_votes__unique_columns(complete_votes_df):
    assert complete_votes_df.columns.value_counts().max() == 1
    
def test__complete_votes__column_types(complete_votes_df):
    EXPECTED_COLTYPES = {
        'proposal_id': 'int64',
        'proposal_title': 'object',
        'validator_address': 'object',
        'validator_name': 'object',
        'vote': 'object',
    }
    actual_coltypes = complete_votes_df.dtypes.astype('str').to_dict()
    invalid_list = [{k:v} for k,v in EXPECTED_COLTYPES.items() if actual_coltypes[k] != EXPECTED_COLTYPES[k]]
    assert len(invalid_list) == 0
    
def test__complete_votes__not_null(complete_votes_df):
    assert complete_votes_df.notnull().mean().mean() == 1

def test__complete_votes__validator_address__is_valid(complete_votes_df):
    invalid_list = [v for v in complete_votes_df.loc[:,'validator_address'] if len(v) != 50 or v[:11] != 'osmovaloper']
    assert len(invalid_list) == 0, f'Invalid addresses found, e.g. {invalid_list[:3]}.'

def test__complete_votes__validator_name__not_blank(complete_votes_df):
    assert (complete_votes_df.loc[:,'validator_name'].str.len() > 0).mean() == 1.0
    
def test__complete_votes__proposal_id__positive_number(complete_votes_df):
    assert (complete_votes_df.loc[:,'proposal_id'] > 0).mean() == 1.0
    
def test__complete_votes__proposal_title__not_blank(complete_votes_df):
    assert (complete_votes_df.loc[:,'proposal_title'].str.len() > 0).mean() == 1.0

def test__complete_votes__vote__is_valid(complete_votes_df, valid_votes):
    assert set(complete_votes_df.loc[:,'vote'].value_counts().index) == set(valid_votes)

    
def test__voting_history__row_count(proposals, voting_history_df):
    assert len(proposals) == voting_history_df.shape[0]
    
def test__voting_history__column_count(validator_selection, voting_history_df):
    assert len(validator_selection) == voting_history_df.shape[1]
    
def test__voting_history__validator_columns(validator_selection, voting_history_df):
    selected_validator_names = sorted([x['name'] for x in validator_selection])
    df_column_names = sorted(voting_history_df.columns.tolist())
    assert selected_validator_names == df_column_names
    
def test__voting_history__validator_indexes(voting_history_df):
    assert sorted(list(voting_history_df.index.names)) == ['id','title']
    
def test__voting_history__index0__positive_integer(voting_history_df):
    invalid_list = [x[0] for x in voting_history_df.index if not x[0] > 0]
    assert len(invalid_list) == 0
    
def test__voting_history__index1__not_blank_str(voting_history_df):
    invalid_list = [x[1] for x in voting_history_df.index if not len(x[1]) > 0]
    assert len(invalid_list) == 0

def test__voting_history__is_valid_votes(voting_history_df, valid_votes):
    vote_labels = []
    for idx in range(voting_history_df.shape[1]):
        vote_labels += list(voting_history_df.iloc[:,idx].value_counts().to_dict().keys())

    assert set(vote_labels).issubset(set(valid_votes))
        
        
def test__formatted_voting_history__row_count(proposals, formatted_voting_history_df):
    assert len(proposals) == formatted_voting_history_df.shape[0]

def test__formatted_voting_history__column_count(validator_selection, formatted_voting_history_df):
    assert len(validator_selection) == formatted_voting_history_df.shape[1]

def test__formatted_voting_history__validator_columns(validator_selection, formatted_voting_history_df):
    # First 10 characters only, in correct order
    selected_validator_names = [x['name'][:10].strip() for x in validator_selection]
    df_column_names = [x[:10].strip() for x in formatted_voting_history_df.columns]
    assert selected_validator_names == df_column_names

def test__formatted_voting_history__validator_indexes(formatted_voting_history_df):
    assert sorted(list(formatted_voting_history_df.index.names)) == ['ID','Proposal']

def test__formatted_voting_history__index0__positive_integer(formatted_voting_history_df):
    invalid_list = [x[0] for x in formatted_voting_history_df.index if not int(x[0].strip()) > 0]
    assert len(invalid_list) == 0
    
def test__formatted_voting_history__index1__prop_prefix(formatted_voting_history_df):
    invalid_list = [x[1] for x in formatted_voting_history_df.index if x[1][:6] != 'Prop #']
    assert len(invalid_list) == 0

def test__formatted_voting_history__is_valid_votes(formatted_voting_history_df, valid_votes):
    vote_labels = []
    for idx in range(formatted_voting_history_df.shape[1]):
        vote_labels += list(formatted_voting_history_df.iloc[:,idx].value_counts().to_dict().keys())

    assert set(vote_labels).issubset(set(valid_votes+['-']))

    
def test__similarity__row_count(similarity_df, validator_selection):
    assert similarity_df.shape[0] == len(validator_selection)

def test__similarity__column_count(similarity_df, validator_selection):
    assert similarity_df.shape[1] == len(validator_selection)

def test__similarity__row_names(similarity_df, validator_selection):
    assert similarity_df.index.tolist() == [x['name'] for x in validator_selection]

def test__similarity__column_names(similarity_df, validator_selection):
    assert similarity_df.columns.tolist() == [x['name'] for x in validator_selection]

def test__similarity__min_value(similarity_df, validator_selection):
    assert similarity_df.min().min() >= 0.0

def test__similarity__max_value(similarity_df, validator_selection):
    assert similarity_df.max().max() == 100.0
