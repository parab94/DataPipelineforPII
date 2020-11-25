import boto3
from boto3.dynamodb.conditions import Key, Attr
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

# Route to the homepage - does not require authentication
app = FastAPI()
@app.get("/", tags=["Homo"])
def read_root():
    return "Welcome to API homepage!"

from v1.routers import router
from mangum import Mangum

# parameters for authentication
API_KEY = "123abc"
API_KEY_NAME = "access_token"
COOKIE_DOMAIN = "localtest.me"

userRegion = "us-east-1"
userClientId = "4hkma6pavubar061g3u11fek9q"
usrPoolId= "us-east-1_o7TlGk5JE"
cidp = boto3.client('cognito-idp')
auth = Cognito(region= userRegion, userPoolId= usrPoolId)
getUser = CognitoCurrentUser(region= userRegion, userPoolId= usrPoolId)

app = FastAPI(title='Api for PII de-identify and re-identify',
              description='de-identification and re-identification using Amazon Comprehend')
app.include_router(router, prefix="/v1")

# Generate JWT Token
@app.get("/tokens", tags=["Generate TOkens"])
async def generate_JWT_token(usrName: str, usrPassword: str):
    JWT = cidp.admin_initiate_auth(UserPoolId= usrPoolId, ClientId= userClientId, AuthFlow= "ADMIN_NO_SRP_AUTH", AuthParameters= { "USERNAME": usrName, "PASSWORD": usrPassword })   
    AccessToken = JWT["AuthenticationResult"]["AccessToken"]
    RefreshToken = JWT["AuthenticationResult"]["RefreshToken"]
    IDToken = JWT["AuthenticationResult"]["IdToken"]
    refreshToken = cidp.admin_initiate_auth(UserPoolId= usrPoolId, ClientId= userClientId, AuthFlow= "REFRESH_TOKEN_AUTH", AuthParameters= {"REFRESH_TOKEN" : RefreshToken})
    dynamodb = boto3.resource('dynamodb')
    refreshToken = refreshToken["AuthenticationResult"]["IdToken"]
    table = dynamodb.Table('Tokens') 
    response = table.update_item(Key = {'Username': usrName},
        UpdateExpression="set RefreshToken=:r,JWT=:t,AccessToken=:a,IDToken=:i",
        ExpressionAttributeValues={
            ':t':JWT,
            ':a': AccessToken,
            ':r': refreshToken,
            ':i': IDToken
        }
    )
    result = "Tokens Created"
    return response,result,refreshToken







# to make it work with Amazon Lambda, we create a handler object
# handler = Mangum(app=app)
