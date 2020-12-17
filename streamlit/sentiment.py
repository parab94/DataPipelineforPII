# import loginstatus,streamlit as st
# import requests
# import json
# import loginstatus
# import boto3
# import streamlit as st
# import nltk
# import tensorflow as tf
# import base64
# def app():
    
#     def _bytes_feature(value):
#         return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
#     def serialize_text(text):
#         example = tf.train.Example(
#             features=tf.train.Features(feature={"text": _bytes_feature(text)})
#         )
#         serialized_example = example.SerializeToString()
#         return serialized_example
#     model_server_url = "http://localhost:8501/v1/models/half_plus_two:predict"
#     def predict(text):
#         example = serialize_text(text)
#         json_data = {
#             "signature_name": "serving_default",
#             "instances": [{"examples": {"b64": base64.b64encode(example).decode("utf-8")}}],
#         }
#         resp = requests.post(model_server_url, json=json_data)
#         return resp.json()
#     # st.write("Test")

#     def get_data(filename):
#         s3 = boto3.client("s3")
#         bucket = "ass2deidentifiedmessage"
#     # filename = "transcript1"  #input from user
#         key = filename + ".txt"
#         file = s3.get_object(Bucket=bucket, Key=key)
#         paragraph = str(file['Body'].read())
#         return paragraph
#     def initiate(filename):
#         whole_text = get_data(filename)
#         text_lines = nltk.tokenize.sent_tokenize(whole_text)
#         for i in range(4,len(text_lines)-96):
#             st.write(text_lines[i])
#             # st.write(i)
#             try:
#                 positive = predict(bytes(text_lines[i], encoding='utf8'))['predictions'][0][0]
#             except:
#                 positive = "Timeout Error"
#             st.write("Positive", positive, "Negative", 1-positive)


#     # initiate("transcript1")
#     st.title('Sentiment Prediction')
#     st.write('Welcome to the Sentiment Analysis page')
#     input_filename = st.text_input("Enter filename here", value='', max_chars=None)
#     local_filename = "transcript1"
#     if st.button('Predict Sentitment'):
#         if loginstatus.status == True:
#             if (input_filename == local_filename):
#                 initiate(input_filename)
#             else:
#                 st.write("This file does not exist")
#         else:
#             st.write("please authenticate user and try again")