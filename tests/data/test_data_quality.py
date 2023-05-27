import pytest
from utils.data import get_validators, get_proposals, get_validator_votes, fetch_datasets


@pytest.fixture
def validators():
    return get_validators()

@pytest.fixture
def proposals():
    return get_proposals()

@pytest.fixture
def votes():
    return get_validator_votes()


# Validators
def test__get_validators__valid_addresses(validators):
    invalid_list = [v['address'] for v in validators if len(v['address']) != 50 or v['address'][:11] != 'osmovaloper']
    assert len(invalid_list) == 0, f'Invalid addresses found, e.g. {invalid_list[:3]}.'

def test__get_validators__non_empty_names(validators):
    invalid_list = [v for v in validators if len(v['name']) == 0]
    assert len(invalid_list) == 0, f'Blank names found, e.g. {invalid_list[:3]}.'
    
def test__get_validators__unique_addresses(validators):
    addresses = [v['address'] for v in validators]
    n = len(addresses)
    n_unique = len(set(addresses))
    assert n == n_unique, f'{n - n_unique} duplicate addresses found.'
    
def test__get_validators__unique_names(validators):
    names = [v['name'] for v in validators]
    n = len(names)
    n_unique = len(set(names))
    assert n == n_unique, f'{n - n_unique} duplicate names found.'

    
# Proposals
def test__get_proposals__unique_ids(proposals):
    ids = [p['id'] for p in proposals]
    n = len(ids)
    n_unique = len(set(ids))
    assert n == n_unique, f'{n - n_unique} duplicate IDs found.'

def test__get_proposals__non_empty_titles(proposals):
    invalid_list = [p['title'] for p in proposals if len(p['title']) == 0]
    assert len(invalid_list) == 0, f'Blank titles found, e.g. {invalid_list[:3]}.'


# Votes
def test__get_validator_votes__validator_address__is_valid(votes):
    invalid_list = [v['validator_address'] for v in votes if len(v['validator_address']) != 50 or v['validator_address'][:11] != 'osmovaloper']
    assert len(invalid_list) == 0, f'Invalid addresses found, e.g. {invalid_list[:3]}.'

def test__get_validator_votes__vote__is_valid(votes):
    VALID_VOTES = ('YES','NO', 'NO WITH VETO','ABSTAIN')
    invalid_list = [v for v in votes if v['vote'] not in VALID_VOTES]
    assert len(invalid_list) == 0, f'Invalid votes found, e.g. {invalid_list[:3]}.'
