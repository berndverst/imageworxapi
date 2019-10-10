import os
import uuid
import json
import base64
import logging
import requests
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlockBlobService

import azure.functions as func

base_folder = 'gamedata'
storageAccount = os.environ["StorageAccount"]
storageAccountKey = os.environ["StorageAccountKey"]
storageContainer = os.environ["StorageContainer"]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    body = req.get_json()

    blob_service = BlockBlobService(account_name=storageAccount, account_key=storageAccountKey)

    records = { 'images': [] }

    for item in body['items']:
        # sign
        sign = item['type']

        # image bits
        img = item['image'].replace('data:image/png;base64,', '')
        stream = BytesIO(base64.b64decode(img))
        stream.seek(0)

        # storage path + save
        blob_name = f'{base_folder}/{sign}/{str(uuid.uuid4())}.png'
        blob_service.create_blob_from_stream(storageContainer, blob_name, stream)

        # return image
        path = f'{blob_service.protocol}://{blob_service.primary_endpoint}/{storageContainer}/{blob_name}'
        records['images'].append(path)

    return func.HttpResponse(body=json.dumps(records),
                             headers={ 
                                 'Content-Type': 'application/json', 
                                'Access-Control-Allow-Origin': '*', 
                                'Access-Control-Allow-Credentials': 'true' })
