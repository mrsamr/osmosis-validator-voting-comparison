"""Checks if data extraction functions are able to extract data."""

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

@pytest.fixture
def datasets():
    return fetch_datasets()


# Validators
def test__get_validators__is_list(validators):
    assert type(validators) == list
    
def test__get_validators__result_count(validators):
    assert len(validators) > 350
    
def test__get_validators__is_list_of_dicts(validators):
    invalid_list = [v for v in validators if type(v) != dict]
    assert len(invalid_list) == 0

def test__get_validators__field_names(validators):
    FIELD_NAMES = ('address','name')
    invalid_list = [v for v in validators if not set(FIELD_NAMES).issubset(set(v.keys()))]
    assert len(invalid_list) == 0, f'Invalid metadata found for {len(invalid_list)} validators, e.g. {invalid_list[0]}. Expected fields: {FIELD_NAMES}'

def test__get_validators__string_addresses(validators):
    invalid_list = [v for v in validators if type(v['address']) != str]
    assert len(invalid_list) == 0

def test__get_validators__string_names(validators):
    invalid_list = [v for v in validators if type(v['name']) != str]
    assert len(invalid_list) == 0
    
    
# Proposals
def test__get_proposals__is_list(proposals):
    assert type(proposals) == list
    
def test__get_proposals__result_count(proposals):
    assert len(proposals) >= 460
    
def test__get_proposals__is_list_of_dicts(proposals):
    invalid_list = [p for p in proposals if type(p) != dict]
    assert len(invalid_list) == 0
    
def test__get_proposals__field_names(proposals):
    FIELD_NAMES = ('id','title')
    invalid_list = [p for p in proposals if not set(FIELD_NAMES).issubset(set(p.keys()))]
    assert len(invalid_list) == 0, f'Invalid metadata found for {len(invalid_list)} validators, e.g. {invalid_list[0]}. Expected fields: {FIELD_NAMES}'

def test__get_proposals__positive_integer_ids(proposals):
    invalid_list = [p for p in proposals if type(p['id']) != int or p['id'] <= 0]
    assert len(invalid_list) == 0
    
def test__get_proposals__string_titles(proposals):
    invalid_list = [p for p in proposals if type(p['title']) not in (str, type(None))]  # Relax criteria for nulls
    assert len(invalid_list) == 0


# Votes
def test__get_validator_votes__is_list(votes):
    assert type(votes) == list
    
def test__get_validator_votes_proposals__result_count(votes):
    assert len(votes) >= 33700
    
def test__get_validator_votes_proposals__is_list_of_dicts(votes):
    invalid_list = [v for v in votes if type(v) != dict]
    assert len(invalid_list) == 0
    
def test__get_validator_votes_proposals__field_names(votes):
    FIELD_NAMES = ('validator_address','proposal_id','vote')
    invalid_list = [v for v in votes if not set(FIELD_NAMES).issubset(set(v.keys()))]
    assert len(invalid_list) == 0, f'Invalid metadata found for {len(invalid_list)} validators, e.g. {invalid_list[0]}. Expected fields: {FIELD_NAMES}'

def test__get_validator_votes__validator_address__is_string(votes):
    invalid_list = [v for v in votes if type(v['validator_address']) != str]
    assert len(invalid_list) == 0

def test__get_validator_votes__proposal_id__is_positive_integer(votes):
    invalid_list = [v for v in votes if type(v['proposal_id']) != int or v['proposal_id'] <= 0]
    assert len(invalid_list) == 0
    
def test__get_validator_votes__vote__is_string(votes):
    invalid_list = [v for v in votes if type(v['vote']) != str]
    assert len(invalid_list) == 0