from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
import csv
import json, os
import requests
import base64
import logging
from django_server.server.api.serializers import (
    TextInputSerializer,
    UploadFileSerializer,
)
from keras.models import load_model
import transformers
import os
from django.core.files import File
import numpy
import mysql.connector

class CollectFeedbackViewSet(ViewSet):
   
    @swagger_auto_schema(query_serializer=TextInputSerializer)
    def create(self, request):
        try:
            count = 894
            text = request.GET.get("file")
            smell = request.GET.get("smell")
            isSmell = request.GET.get("isSmell")
            print('response : '+text+' , '+smell+' , '+isSmell)
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
