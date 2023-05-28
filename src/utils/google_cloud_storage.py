"""Google Cloud Storage helper functions"""


import os
import json
from google.cloud import storage
from pandas import to_datetime


def upload_file_to_gcs(file, bucket_name, object_key, service_account_info):
    """Uploads a file to Google Cloud Storage.

    Parameters
    ----------
    file : str
        The local path of the file to upload.
        
    bucket_name : str
        The name of the bucket to upload the file to.
        
    object_key : str
        The name to give the uploaded file in the bucket.
        
    service_account_info :dict
        The service account JSON key file contents as a dictionary.
        
    Returns
    -------
    None
    
    """
    
    if object_key is None:
        object_key = file.split('/')[-1]
    
    # Instantiate a storage client using the service account info dictionary
    storage_client = storage.Client.from_service_account_info(service_account_info)

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object
    blob = bucket.blob(object_key)

    # Upload the file
    blob.upload_from_filename(file)

    print(f"File {file} uploaded to {bucket_name}/{object_key}.")