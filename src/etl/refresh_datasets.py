"""Extracts fresh datasets from source and loads to cloud storage"""


import json
import gzip
import os
from src.utils.atomscan import get_validators
from src.utils.flipside_crypto import query
from src.utils.google_cloud_storage import upload_file_to_gcs


def save_dict_to_gzip_json(dictionary, filename):
    with gzip.open(filename, 'wt') as file:
        json.dump(dictionary, file)
        
        
def read_sql_statement(file_path):
    with open(file_path, 'r') as file:
        sql_statement = file.read()
    return sql_statement
        

def refresh_datasets(bucket_name, service_account_key):
    
    SQL_FILE_PROPOSALS = 'src/sql/proposals.sql'
    SQL_FILE_VOTES = 'src/sql/votes.sql'
    
    VALIDATORS_FILENAME = 'data/validators.json.gz'
    PROPOSALS_FILENAME = 'data/proposals.json.gz'
    VOTES_FILENAME = 'data/votes.json.gz'
    
    # Extract validators list from Atomscan
    validators = get_validators()
    
    # Extract proposals list from Flipside
    sql_stmt_proposals = read_sql_statement(SQL_FILE_PROPOSALS)
    proposals = query(sql_stmt_proposals, return_df=False)
    
    # Extract votes dataset from Flipside
    sql_stmt_votes = read_sql_statement(SQL_FILE_VOTES)
    votes = query(sql_stmt_votes, return_df=False)

    # Save to local files
    save_dict_to_gzip_json(validators, VALIDATORS_FILENAME)
    save_dict_to_gzip_json(proposals, PROPOSALS_FILENAME)
    save_dict_to_gzip_json(votes, VOTES_FILENAME)


    # Upload files to cloud storage
    upload_file_to_gcs(file=VALIDATORS_FILENAME,
                       bucket_name=bucket_name,
                       object_key=VALIDATORS_FILENAME,
                       service_account_key=service_account_key)

    upload_file_to_gcs(file=PROPOSALS_FILENAME,
                       bucket_name=bucket_name,
                       object_key=PROPOSALS_FILENAME,
                       service_account_key=service_account_key)

    upload_file_to_gcs(file=VOTES_FILENAME,
                       bucket_name=bucket_name,
                       object_key=VOTES_FILENAME,
                       service_account_key=service_account_key)
    

if __name__ == '__main__':
    
    SERVICE_ACCOUNT_KEY = 'credentials/service_account_key.json'
    
    # Load secrets from environment variables
    gcs_bucket = os.environ['GCS_BUCKET']

    # Run ETL job
    refresh_datasets(bucket_name=gcs_bucket,
                     service_account_key=SERVICE_ACCOUNT_KEY)