"""Extracts fresh datasets from source and loads to cloud storage"""


import json
import gzip
import argparse
from src.utils.flipside import get_validators_from_api, get_proposals_from_api, get_validator_votes_from_api
from src.utils.google_cloud_storage import upload_file_to_gcs


def save_dict_to_gzip_json(dictionary, filename):
    with gzip.open(filename, 'wt') as file:
        json.dump(dictionary, file)
        

def refresh_datasets(bucket_name, service_account_info):
    
    VALIDATORS_FILENAME = 'data/validators.json.gz'
    PROPOSALS_FILENAME = 'data/proposals.json.gz'
    VOTES_FILENAME = 'data/votes.json.gz'

    
    # Extract datasets from source
    validators = get_validators_from_api()
    proposals = get_proposals_from_api()
    votes = get_validator_votes_from_api()


    # Save to local files
    save_dict_to_gzip_json(validators, VALIDATORS_FILENAME)
    save_dict_to_gzip_json(proposals, PROPOSALS_FILENAME)
    save_dict_to_gzip_json(votes, VOTES_FILENAME)


    # Upload files to cloud storage
    upload_file_to_gcs(file=VALIDATORS_FILENAME,
                       bucket_name=bucket_name,
                       object_key=VALIDATORS_FILENAME,
                       service_account_info=service_account_info)

    upload_file_to_gcs(file=PROPOSALS_FILENAME,
                       bucket_name=bucket_name,
                       object_key=VALIDATORS_FILENAME,
                       service_account_info=service_account_info)

    upload_file_to_gcs(file=VOTES_FILENAME,
                       bucket_name=bucket_name,
                       object_key=VALIDATORS_FILENAME,
                       service_account_info=service_account_info)
    

if __name__ == '__main__':
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(prog='refresh_datasets')
    parser.add_argument('--bucket-name', action='store', required=False, default=4, help='The name of the Google Cloud Storage bucket')
    parser.add_argument('--service-account-info', action='store', required=False, default=4, help='The content of the Google service account json file')
    args = parser.parse_args()
    

    # Parse service account json string
    service_account_info = json.loads(args.service_account_info)

    
    # Run ETL job
    refresh_datasets(bucket_name=args.bucket_name,
                     service_account_info=service_account_info)