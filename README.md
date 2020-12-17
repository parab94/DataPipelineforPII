# Team 7  - Assignment Part 2!

The goal of this assignment is to create APIs which can -
- Scrape data from a website
- Recognize enitites which can be 
- Anonymize data through Masking and Anonymization
- Deanonymize fields that can be deanonymized

Additionally, we will create a **Streamlit** interface where we will test the APIs and display the results.

## Folders and Files

- Streamlit - this folder contains the main page and all the type of views where we will show one API per page 
- Fastapi_lambda - this folder contains the code for the lambda function
- requirements.txt - contains the name and versions of all the packages

## Streamlit  

Streamlit is a python library to easily create big data apps
>**Note**: Run the streamlit app using the command "streamlit run main.py"

Below are all the files and their descriptions in the Streamlit folder  
- main.py- the main page containing the sidebar and page section choose from
- login.py- contains the view to login into the app using AWS Cognito and DynamoDB. We will have to enter the username and the password to login and continue withe running all the tasks/API
- scraping.py- contains the view and API to scrape data from a particular URL. We will enter the URL as the input and then all the scraped data for multiple webpages will be stored in an S3 bucket as txt files
- recognition.py- contains view and API to recognize each entity from the article/text. PII information is detected by the API using AWS Comprehend Service from the text files
- masking.py- contains view and API to mask entitites from the text. The recogized entities will be displayed as masked data in the page after the API is called
- deanonymization.py- contains view and API to de-anonymize entities from te anonymized text. We use a hash algorithm to deanonymize the anonymize data in a previous API and display the data in this page
-sentiment.py- contains view and API to predict sentiment scores fo the deanonymized text. We use tensorflow-serving and docker create a server

Post authentication, each page will check if the user is logged in before actually calling the API. This will ensure that only if the user is logged in, will the data be displayed in the  respective pages.

# AWS Implementation

The FastAPI implementation is packaged using Magnum and deployed on AWS Lambda. this is done by zipping up the main.py file of fast API along with its python dependencies.

## Lambda Implementation

The handler is set to fastApi.handler(wrapped by magnum) and tested and deployed on AWS Lambda. Note: In order to check the code on lambda, the dependencies are added as layers above the the main fastApi file.

## API Gateway Implementation

A RestApi based API is created with complete control over the request and response of API management capabilities. It can be created with first method 'ANY' or 'GET' with integration of Lambda function created in the above step. Then the API is deployed which hits the fastAPI lambda and can be accessed using the link generated. 

## API Description

**Scraping**: This API scrapes data from the website: [https://seekingalpha.com/earnings/earnings-call-transcripts](https://seekingalpha.com/earnings/earnings-call-transcripts "https://seekingalpha.com/earnings/earnings-call-transcripts") using beautifulsoap bs4 library. The data was scraped from each of the links provided on the web page and stored in a S3 bucket in txt file format.

**Entity Recognition**: Here we have read the txt files from the S3 bucket and called the Amazon Comprehend Service to detect the PII information. This identified entities are stored in a S3 bucket

**De-identify**: In this Api the de-identification Step function was leveraged to get the anonymized message.

**Masking**: In this Api the de-identification Step function was leveraged to get the anonymized message.

**Re-identify**: The Api re-identifies the entities from the mentioned text file with the help of the given hash key.

**Prediction**: This API predicts the sentiment score of a sentiment/text