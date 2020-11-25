from fastapi import APIRouter
from typing import Optional
import requests
import boto3
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import io

from fastapi import APIRouter
from typing import Optional
import requests
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


#using AWS service 
s3 = boto3.resource('s3')
s3client = boto3.client('s3')
bucketName = 'ass2transcripts'
bucket = s3.Bucket(bucketName)

router = APIRouter()
url = "http://seekingalpha.com/earnings/earnings-call-transcripts"

userRegion = "us-east-1"
userClientId = "4hkma6pavubar061g3u11fek9q"
usrPoolId= "us-east-1_o7TlGk5JE"
cidp = boto3.client('cognito-idp')
auth = Cognito(region= userRegion, userPoolId= usrPoolId)
getUser = CognitoCurrentUser(region= userRegion, userPoolId= usrPoolId)

# @router.get("/scraping")
# async def scraping_data():
#     for i in range(1,3): #choose what pages of earnings to scrape
#         process_list_page(url,i)

@router.get("/scraping")
async def scraping_data(currentUser: CognitoClaims = Depends(getUser)):
    for i in range(1,3): #choose what pages of earnings to scrape
        process_list_page(url,i)
    return "scraping successful"

def grab_page(url,i,fname):
    print("*********************attempting to grab page: " + url)
    page = requests.get(url)
    page_html = page.text
    #print(page_html)
    soup = BeautifulSoup(page_html, 'html.parser')
    #meta = soup.find("div",{'class':'a-info get-alerts'})
    content = soup.find(id="a-body")
    if type(content) == "NoneType":
        print("------------------skipping this link, no content here")
        return
    else:
        text = content.text
        #mtext = meta.text
        print("**")
        filename = "transcript"+str(i) # + get_date(mtext)
        file = open(filename.lower() + ".txt", 'w')
        file.write(text)
        file.close
        newKey = filename +'.txt'
        s3client.put_object(Bucket= bucketName , Key=newKey, Body=text)
        print(filename.lower()+ "sucessfully saved")

def process_list_page(url,i):
    origin_page = url + "/" + str(i)
    print("getting page " + origin_page)
    page = requests.get(origin_page)
    page_html = page.text
    #print(page_html)
    soup = BeautifulSoup(page_html, 'html.parser')
    alist = soup.find_all("li",{'class':'list-group-item article'})
    print(len(alist))
    for i in range(0,len(alist)):
        print("I work")
        url_ending = alist[i].find_all("a")[0].attrs['href']
        url = "http://seekingalpha.com" + url_ending
        fname = str(url_ending.replace("/article/",""))
        print(url)
        grab_page(url,i,fname)
        time.sleep(3)
    
    

