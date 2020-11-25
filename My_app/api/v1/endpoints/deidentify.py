from fastapi import APIRouter
from typing import Optional
import requests
from .comprehend import detect_pii, datachunk
import boto3
from botocore.vendored import requests
import pandas as pd
import json
import hashlib
import uuid

import boto3
import time
# from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import io
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

userRegion = "us-east-1"
userClientId = "4hkma6pavubar061g3u11fek9q"
usrPoolId= "us-east-1_o7TlGk5JE"
cidp = boto3.client('cognito-idp')
auth = Cognito(region= userRegion, userPoolId= usrPoolId)
getUser = CognitoCurrentUser(region= userRegion, userPoolId= usrPoolId)


router = APIRouter()

#using AWS service 
s3 = boto3.resource('s3')
s3client = boto3.client('s3')
comprehend_client = boto3.client('comprehend')
bucket = s3.Bucket('ass2transcripts')
bucket2 = s3.Bucket('ass2deidentified')


@router.get("/de-identify")
async def deidentify(currentUser: CognitoClaims = Depends(getUser)):
    for obj in bucket.objects.all():
      key = obj.key  
      print(key)  
      fileobj = s3client.get_object(Bucket='ass2transcripts', Key=key) 
      filedata = fileobj['Body'].read()
          # # file data will be a binary stream.  We have to decode it 
      text = filedata.decode('utf-8') 
      entity_list = detect_pii(text)
      # for entity in entity_list:
      #     print(entity)
      anonymized_text, df = deidentify_entities_in_message(text, entity_list)
      print(anonymized_text)
      s3client.put_object(Bucket= 'ass2deidentified', Key=key[:-4]+".csv", Body= df.to_csv(index=False))
    return "he"



def deidentify_entities_in_message(message, entity_list):
    entity_map = dict()
    for entity in entity_list:

      if entity['Type'] == 'PERSON' or entity['Type'] == 'LOCATION' :
        salted_entity = entity['Text'] + str(uuid.uuid4())
        hashkey = hashlib.sha256(salted_entity.encode()).hexdigest()
        replace_key = hashkey[:8]
        
      elif entity['Type'] == 'QUANTITY' and entity['Text'][-1] == '%':
        salted_entity = entity['Text'] + str(uuid.uuid4())
        hashkey = entity['Text']
        replace_key  = "*******"
       
      else :
        salted_entity = entity['Text'] + str(uuid.uuid4())
        hashkey = entity['Text']
        replace_key  = entity['Text']
        
        

      entity_map[entity['Text']] = hashkey
      
      message = message.replace(entity['Text'], replace_key)
      df = pd.DataFrame(list(entity_map.items()), columns=['Text', 'Hashkey'])
      
      print(message)
      print(entity_map)
    return message, df



    

