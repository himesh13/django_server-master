from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
import csv
import pandas as pd
import uuid
import json, os, shutil
import requests
import base64
import logging
from django_server.server.api.serializers import (
    TextInputSerializer,
    UploadFileSerializer,
    CollectFeedbackSerializer,
)
from keras.models import load_model
import transformers
import os
from django.core.files import File
import numpy
import mysql.connector

class CollectFeedbackViewSet(ViewSet):
   
    @swagger_auto_schema(query_serializer=CollectFeedbackSerializer)
    def create(self, request):
        try:
            count = 894
            text = request.GET.get("file")
            smell = request.GET.get("smell")
            isSmell = request.GET.get("isSmell")
            print('response : '+text+' , '+smell+' , '+isSmell)

            # to save any file on your current data path you shoud use this relative path:
            # ./app/data/
            # Writing  text field to file
            os.makedirs("./data/code/", exist_ok=True)

            file_name = str(uuid.uuid4())

            with open(f"./data/code/{file_name}.txt", "w") as file:
                # Writing data to a file
                file.write(text)
            print("passes to stage 2")
            # prepare csv file
            try:
                df = pd.read_csv('./data/code/feedback.csv')
                new_df = pd.DataFrame({"file_name": file_name, "smell":str(smell), "isSmell":str(isSmell) }, index=[0])
                merged_df = df.append(new_df)
                merged_df.to_csv("./data/code/feedback.csv", index=None)
            except:
                print("file does not exist --- create it ....")
                df = pd.DataFrame({"file_name": file_name, "smell":str(smell), "isSmell":str(isSmell) }, index=[0])
                df.to_csv("./data/code/feedback.csv", index=None)

            

            # increament vairable
            # we should use a DB to store last value or simple way is to use file
            with open("./data/var") as f:
                var = [line.rstrip() for line in f]
                print(var)
            
            if var:
                incr = int(var[0]) +1
            else:
                incr = 1
            print(incr)

            with open(f"./data/var", "w") as file:
                # Writing data to a file
                file.write(str(incr))

            return HttpResponse(
                status=status.HTTP_200_OK,
            )



            
        except Exception as e:
            print(e)
            return Response(
                
                f"[ERR]: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )




class TextInputViewSet(ViewSet):
    """
    Load Text and Apply ML model API
    """
    autoencoder = load_model( 'lstm_model.h5')
    tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-cased")
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    @swagger_auto_schema(query_serializer=TextInputSerializer)
    def create(self, request):
        try:
            count = 894
            text = request.GET.get("file")
            isClass = request.GET.get("isClass")
            qaulifiedName = request.GET.get("qaulifiedName")
            className = request.GET.get("className")
            print('qualifiedname')
            print(text)
            text = text.replace('\n', ' ').replace('\r', '')
            tokenized_text = self.tokenizer.tokenize(text)
            input_ids = self.tokenizer.convert_tokens_to_ids(tokenized_text)
            print('idssss')
           
            X_train = numpy.array(input_ids,dtype=float)
            h = X_train.shape[0]
            w = count - h
            X_train = numpy.pad(X_train,(0,w), 'maximum')
            print(X_train.shape)
            X_train = X_train.reshape(1,count)
            print('Xtrain')
            print(X_train)
            y = self.autoencoder.predict(X_train)
            y = y.reshape(y.shape[0], y.shape[1])   
            mse = numpy.mean(numpy.power(X_train - y, 2), axis=1)                            
            print(mse)
            y_pred = [1 if e > 400000 else 0 for e in mse]
            print('result')
            print(y_pred)

            return HttpResponse(
                json.dumps({"is_file_uploaded":True, "isSmell": y_pred}),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            return Response(
                
                f"[ERR]: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )

class LoadDataFilesViewSet(ViewSet):
    
    serializer_class = UploadFileSerializer

    @swagger_auto_schema()
    def create(self, request):
        print('in load data')
        try:
            print('trying to read file')
            method_file_uploaded = request.FILES.get("methodFile")
            print('trying to read class file')
            class_file_uploaded = request.FILES.get("classFile")
        except Exception as e:
            logging.exception(f"Failed to get Uploaded File ! ::: > {e}")
            return Response(
                f"[ERR] file data should be passed on file field: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        line_count_meth = 0
        for row in method_file_uploaded:
            if line_count_meth == 0:
                print(row)
            line_count_meth += 1
        line_count_class = 0
        for row in class_file_uploaded:
            if line_count_class == 0:
                print(row)
            line_count_class += 1    
        
        print('length'+str(line_count_meth)+" and "+str(line_count_class))

        return HttpResponse(
                status=status.HTTP_200_OK,
            )
        
class LoadFileViewSet(ViewSet):
    """
    Load File and Apply Prediction API
    """

    serializer_class = UploadFileSerializer
#     mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="root",
#   database="plugin"
# )
    @swagger_auto_schema()
    def create(self, request):
        try:
            file_uploaded = request.FILES.get("file")
        except Exception as e:
            logging.exception(f"Failed to get Uploaded File ! ::: > {e}")
            return Response(
                f"[ERR] file data should be passed on file field: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # no exception:
            # [stage 1] save file
            with open(
                "django_server/server/api/data/decoded.pdf", "wb"
            ) as my_file:
                my_file.write(file_uploaded.read())

            # [stage 2] load file to apply some ML models
            with open(
                "django_server/server/api/data/decoded.pdf", "rb"
            ) as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode("ascii")

            ############################################################################
            ####### place you model application here [use encoded_string] ##############
            ############################################################################
            os.remove("django_server/server/api/data/decoded.pdf")
            return HttpResponse(
                json.dumps({"is_file_uploaded":True, "prediction": "uploadfile_api"}),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                f"[ERR]: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
