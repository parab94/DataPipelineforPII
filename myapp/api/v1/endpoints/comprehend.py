from fastapi import APIRouter
from typing import Optional
import requests
import boto3
from botocore.vendored import requests
import pandas as pd
from fastapi import APIRouter
from typing import Optional
import requests
import boto3
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import io
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

router = APIRouter()


userRegion = "us-east-1"
userClientId = "4hkma6pavubar061g3u11fek9q"
usrPoolId= "us-east-1_o7TlGk5JE"
cidp = boto3.client('cognito-idp')
auth = Cognito(region= userRegion, userPoolId= usrPoolId)
getUser = CognitoCurrentUser(region= userRegion, userPoolId= usrPoolId)

#using AWS service 
s3 = boto3.resource('s3')
s3client = boto3.client('s3')
comprehend_client = boto3.client('comprehend')
bucket = s3.Bucket('ass2transcripts')
ddb = boto3.client('dynamodb')

@router.get("/comprehend")
async def comprehend_files(currentUser: CognitoClaims = Depends(getUser)):
    for obj in bucket.objects.all():
        key = obj.key  
        print(key)  
        fileobj = s3client.get_object( Bucket='ass2transcripts',Key=key) 
        filedata = fileobj['Body'].read()
        text = filedata.decode('utf-8') 
        entity_list = detect_pii(text)
        textEntities = [dict_item['Text'] for dict_item in entity_list]
        typeEntities = [dict_item['Type'] for dict_item in entity_list]
        d = {'Type' : typeEntities, 'Text' : textEntities }
        df= pd.DataFrame(data=d)
        s3client.put_object(Bucket= 'ass2detectedentity', Key=key[:-4]+".csv", Body= df.to_csv(index=False))
    return 


def datachunk(para):
    text_list=[]
    while para:
        text_list.append(str(para[:4500]))
        para = para[4500:]

    return text_list[:25]

def detect_pii(text):
    entities = []
    entity_list = comprehend_client.batch_detect_entities(TextList = datachunk(text) , LanguageCode = 'en') #API call for entity extraction
    print(len(entity_list['ResultList']))
    for i in range(len(entity_list['ResultList'])):
        for j in range(len(entity_list['ResultList'][i]['Entities'])):
            entities.append(entity_list['ResultList'][i]['Entities'][j])
    ##print(entities)
     #the text that has been identified as entities
     #the type of entity the text is

    return entities



