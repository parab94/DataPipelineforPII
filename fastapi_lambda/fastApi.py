import boto3, json, uuid, os, time, io 
from mangum import Mangum
from pydantic import BaseModel, Field
from typing import Optional
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse
from bs4 import BeautifulSoup 
import requests, numpy
from mangum import Mangum
from urllib.parse import urlparse,urlsplit
from boto3.dynamodb.conditions import Key
import pandas as pd
# Route to the homepage - does not require authentication
#app = FastAPI()
app = FastAPI(openapi_prefix="/prod")

s3 = boto3.resource('s3')
s3client = boto3.client('s3')
ddb = boto3.resource('dynamodb')
comprehend_client = boto3.client('comprehend')


bucket = s3.Bucket('ass2transcripts')
table = ddb.Table('DeidentificationTable')

@app.get("/", tags=["Hompage"])
def read_root():
    return "Welcome to API homepage!"

@app.get("/authenticate")
async def authenticate(username: str, password: str):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('User_details')
    OTP = username
    print("here")
    response = table.get_item(Key = {'Username': OTP})
    #make str
    response = str(response)
    fullstring = response
    substring = "Password"
    if substring in fullstring:
        
        verified = "True"
        response = "Congratulations User Verified!!"
        print(verified)
    else:
        verified = "False"
        response = "Please enter valid username/password!!"
        print(verified)
    return verified


@app.get("/scrapeCallTranscripts", tags=["Scrape Call Transcripts"])
async def scrape_call_transcript(url):
    
    def grab_page(url,url_ending,alist):
        
        print("attempting to grab page: " + url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'Connection' : 'keep-alive',
        'Content-Length' : '799',
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8,hi;q=0.7,mr;q=0.6'
        }
        page = requests.get(url + "/", headers = headers, timeout=5)
        page_html = page.text
        soup = BeautifulSoup(page_html, 'html.parser')
        # meta = soup.find("div",{'class':'a-info get-alerts'})
        content = soup.find(id="a-body")        
        if content == None :
            print("Skipping this")
        else:
            text = content.text
            #AWS
            outbucket = 'ass2transcripts'
            s3 = boto3.resource('s3')
            outfile = io.StringIO(text)
            # Generate output file and close it!
            outobj = s3.Object(outbucket,url_ending+'.txt')
            outobj.put(Body=outfile.getvalue())
            outfile.close()
            
            

    def process_list_page(url,k):
        origin_page = url + "/" + str(k)
        print("getting page " + origin_page)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}
        page = requests.get(origin_page, headers = headers)
        page_html = page.text
        soup = BeautifulSoup(page_html, 'html.parser')
        alist = soup.find_all("li",{'class':'list-group-item article'})
        for i in range(0,len(alist)):
            url_ending = alist[i].find_all("a")[0].attrs['href']
            parser = urlsplit(url)
            header = parser [0]
            base = parser [1]
            header=str(header)
            base=str(base)
            url = header + "://" + base + url_ending
            # url = "http://seekingalpha.com" + url_ending
            print("************")
            url_ending = str(url_ending.replace("/article/",""))
            print(url_ending)
            grab_page(url,url_ending,alist)
            time.sleep(.5)

    for i in range(1,3): #Page Range
        process_list_page(url,i)
    result = "All files Uploaded"
    return result


#Comprehend
@app.get("/comprehend")
async def comprehend_files():

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

    bucket = s3.Bucket('onefilescrapedbucket')
    for obj in bucket.objects.all():
        key = obj.key  
        print(key)  
        fileobj = s3client.get_object( Bucket='onefilescrapedbucket',Key=key) #bucket 
        filedata = fileobj['Body'].read()
        text = filedata.decode('utf-8') 
        entity_list = detect_pii(text)
        textEntities = [dict_item['Text'] for dict_item in entity_list]
        typeEntities = [dict_item['Type'] for dict_item in entity_list]
        d = {'Type' : typeEntities, 'Text' : textEntities }
        trying = json.dumps(d)
        df = pd.DataFrame(data=d)
        s3client.put_object(Bucket= 'ass2detectedentity', Key=key[:-4]+".csv", Body= df.to_csv(index=False))
    return trying
    
#de-identify
@app.get("/de-identify")
async def deidentify(ExeName: str, keyname : str):
    #arn:aws:states:us-east-1:198250712026:stateMachine:DeIdandMaskStateMachine-V9YcZVzewMXk
    import boto3,json,time
    print("1")
    # The Amazon Resource Name (ARN) of the state machine to execute.
    STATE_MACHINE_ARN = 'arn:aws:lambda:us-east-1:362654931460:function:MaskOrDeidentify'
    #The name of the execution user input
    EXECUTION_NAME = ExeName #u have to take this from user ...
    #reading the file to be deidentified
    #key = "4391288-burlington-stores-inc-burl-ceo-michael-osullivan-on-q3-2020-results-earnings-call-transcript.txt"
    key = keyname  + ".txt"
    print("2")
    fileobj = s3client.get_object(Bucket='ass2transcripts',Key=key) 
    filedata = fileobj['Body'].read()
    text = filedata.decode('utf-8') 
    
    print("3")
    #The string that contains the JSON input data for the execution
    inputJSON = { "message": text[:20000]}

    INPUT = json.dumps(inputJSON)

    sfn = boto3.client('stepfunctions')
    print("4")
    response = sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=EXECUTION_NAME,
        input=INPUT
    )
    print("5")
    #display the arn that identifies the execution
    executionARN = response.get('executionArn')
    print("running with Mask")
    #waiting
    time.sleep(1)
    print("wait....")
    time.sleep(5)
    print("wait....")
    time.sleep(4)
    print("wait....")
    #getting actual response
    response = sfn.get_execution_history(
        executionArn=executionARN,
        maxResults=1,
        reverseOrder=True,
        includeExecutionData=True
    )
    print(response)
    outputString = response.get('events')[0].get('executionSucceededEventDetails').get('output')
    dictOutput = json.loads(outputString)
    #print(dictOutput)
    hash_message = dictOutput.get('hashed_message')
    hash = str(hash_message).replace('hashed_message','')
    print(hash)
    print("************************")
    deid_message = dictOutput.get('deid_message')
    message = str(deid_message).replace('deid_message','')
    print(message)
    s3client.put_object(Bucket= 'ass2deidentifiedmessage', Key=key[:-4]+".txt", Body=message )
    return hash

#Mask
# @app.get("/maskEntities", tags=["Anonymize Entities"])
# def maskEntities(verified: bool, fileName:str, entityList: str, maskCharacter):
#     comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
#     inputBucket = f"s3://scrapecalldata/{fileName}.txt" #your bucket for input 
#     response = comprehend.start_pii_entities_detection_job(
#     InputDataConfig={
#     'S3Uri': inputBucket,
#     'InputFormat': 'ONE_DOC_PER_LINE'
#     },
#     OutputDataConfig={
#     'S3Uri': 's3://identifyentity/', #your bucket for output
#     },
#     Mode='ONLY_REDACTION',
#     RedactionConfig={
#     'PiiEntityTypes': [
#     entityList
#     ],
#     'MaskMode': 'MASK',
#     'MaskCharacter': maskCharacter
#     },
#     DataAccessRoleArn='arn:aws:iam::198250712026:role/service-role/AmazonComprehendServiceRole-PIIRole' #User your comprehend role,
#     JobName='comprehend-REDACTnew',
#     LanguageCode='en'
#     )
#     jobID = response['JobId']
#     return jobID
    
#reidentify
@app.get("/reIdentifyEntities", tags=["Reidentify"])
async def reIdentifyEntities(Hash: str,filename: str): 
    dynamodb = boto3.resource('dynamodb')
    dynamodbClient = boto3.client("dynamodb")
    table = dynamodb.Table('DeidentificationTable')
    #Hash = "2011fb96f76ea78102ea42058c7b6072e437a63f4a59a6b49391e9954e982e51" # input from user
    #Query as per user hashhtsl
    # #getting user deidentified_message from s3
    s3 = boto3.client("s3")
    bucket = "ass2deidentifiedmessage"
   # filename = "transcript1"  #input from user
    key = filename + ".txt"
    file = s3.get_object(Bucket=bucket, Key=key)
    paragraph = str(file['Body'].read())
    print(Hash)
    #paragraph = str(file['Body']['deidentified_message'].read()) // to use this if the file is jSON
    #replace function with cheap thrills HT
    # message = str(paragraph)
    print("******************Before********************")
    #print(paragraph)
    #paragraph = json.dumps(paragraph)
    Query = table.query(
        IndexName = 'MessageHash-index',
        KeyConditionExpression = Key('MessageHash').eq(Hash)
    )
    # message = "Good morning, everyody. My name is 2c9128030504701edc16914de231d68f763f3815fe6414647678a0131545fa4, and today I feel like sharing a whole lot of personal information with you. Let's start with my Email address e937d3c279a947ad702aaf38c74510e93fa0394a13e4d89d0dfcef3f809.com. My address is 46fef4ce65ef72693f7c8748fda309e4cd2667977e2311fdd63968e3c, CA. My phone numer is 06559e1e922c2a4c9804cdd6018a4d01c896550f8da713198cc6012e8c3cc. My Social security numer is 40fcfd205559d58146fed63e7f56c810210e8e2ae9a8868a7427fd23322fe47. My Bank account numer is 38d07d021793837a06298662470a7cecfa2d8e3f2cf09d58e676928527c and routing numer 323cc64d1ea5374d7acc8a731222a281803c974c9a63815c481799487f99675. My credit card numer is f8536c70595fcafc43fc3c727d2dc28cd48fa07481a4c3de86a4cc3, Expiration Date 2737067aa34537cf63c12e0dea260d815acf37e4a97e78f6f8e526a7c91, my C V V code is 121, and my pin 6cf0a992320492346a0881597e3a91e4f21a9818a42d8de5210385531df7195. Well, I think that's it. You know a whole lot aout me. And I hope that f4088903685e44f60185a7ad7a795891ee8394118a7970694fd1a571e823 comprehend is doing a good jo at identifying PII entities so you can redact my personal information away from this document. Let's check."
    tableList = Query.get('Items')
    # print (tableList)

    entityValues = ""
    entityHash = ""
    #print(paragraph)
    for tableItem in tableList:
       # print(entityValues,entityHash)
        entityValues = tableItem.get("Entity")
        entityHash =  tableItem.get("EntityHash")
        # message = message.replace(entityHash,entityValues)
        paragraph = paragraph.replace(entityHash,entityValues)

    for tableItem in tableList:
        
        entityValues = tableItem.get("Entity")
        entityHash =  tableItem.get("EntityHash")
        print(entityValues,entityHash)
        # message = message.replace(entityHash,entityValues)
        paragraph = paragraph.replace(entityHash,entityValues)
    # print (paragraph)
    paragraph = paragraph.replace("b","")
    paragraph = paragraph.replace("\\n", " ")
    # paragraph = paragraph.replace('" ','')
    # paragraph = paragraph.replace('"','')
    print("******************After********************")
    print (paragraph)
    print("Thanks Giving!!!")
    return paragraph

handler = Mangum(app)


