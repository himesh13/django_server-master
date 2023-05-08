import threading
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
from django_server.server.api.MetricModel import MethodMetric, ClassMetric
from django_server.server.Utils import split
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
from django_server.server.api.Metrics import Metrics
from django_server.server.api.EncoderModel import train_model
metrics = Metrics([],[])
class CollectFeedbackViewSet(ViewSet):
    global metrics
    @swagger_auto_schema(query_serializer=CollectFeedbackSerializer)
    def create(self, request):
        try:
            count = 894
            text = request.GET.get("file")
            smell = request.GET.get("smell")
            isSmell = request.GET.get("isSmell")
            userResponded = request.GET.get("userResponded")
            
            print('response : '+text+' , '+smell+' , '+isSmell)

            # to save any file on your current data path you shoud use this relative path:
            # ./app/data/
            # Writing  text field to file
            if(smell == 'ComplexMethod'):
                if(isSmell == 'true'):
                    dataPath = './data/code/ComplexMethod/True'
                    #os.makedirs("./data/code/ComplexMethod/True", exist_ok=True)
                else:
                    dataPath = './data/code/ComplexMethod/False'
                    #os.makedirs("./data/code/ComplexMethod/False", exist_ok=True)
            elif(smell == 'LongMethod'):
                if(isSmell == 'true'):
                    dataPath = './data/code/LongMethod/True'
                else:
                    dataPath = './data/code/LongMethod/False'
            else:
                if(isSmell == 'true'):
                    dataPath = './data/code/MultiFaceted/True'
                else:
                    dataPath = './data/code/MultiFaceted/False'

            os.makedirs(dataPath, exist_ok=True)        
            file_name = str(uuid.uuid4())

            with open(dataPath+'/'+file_name+".txt", "w") as file:
                # Writing data to a file
                file.write(text)
            print("passes to stage 2")
            # prepare csv file
            try:
                df = pd.read_csv('./data/code/feedback.csv')
                new_df = pd.DataFrame({"file_name": file_name, "smell":str(smell), "isSmell":str(isSmell), "userResponded":str(userResponded) }, index=[0])
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
           
            metrics.handleFeedbackCount()
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
    global metrics
    """
    Load Text and Apply ML model API
    """
    autoencoder_cm = load_model('lstm_model.h5')
    autoencoder_lp = load_model('lstm_model_lp.h5')
    autoencoder_abs = load_model('lstm_model_ma.h5')

    tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-cased")
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    @swagger_auto_schema(query_serializer=TextInputSerializer)
    def create(self, request):
        try:
            count = 894
            smell = ""
            text = request.GET.get("file")
            isClass = request.GET.get("isClass")
            qaulifiedName = request.GET.get("qaulifiedName")
            className = request.GET.get("className")
            methodName = request.GET.get("typeName")
            y_pred = ""
            smell = []
            if(isClass == "False"):
                result,val = metrics.doesExistMethod(split(qaulifiedName,'.',-1)[0],split(qaulifiedName,'.',-1)[1],className)
                
            else:
                result,val = metrics.doesExistClass(qaulifiedName,className)
            print('Result is '+str(result))
            if result == False:
              return HttpResponse(
                json.dumps({"is_file_uploaded":True, "isSmell": False, "smell":smell}),
                status=status.HTTP_200_OK,
            )
            else:
                res = val[0]
                if(isClass == "False"):

                    if((float(res.cc) >= 4 and float(res.cc) <= 6)):
                        y_pred = self.callAlgo(count,text,"ComplexMethod")
                        if y_pred == 1:
                            smell.append("ComplexMethod")
                        elif (float(res.cc) >= 8):
                            smell.append("ComplexMethod")

                    if(int(res.pc) >= 3 and int(res.pc) <= 5):
                        y_pred = self.callAlgo(1074,text,"LongMethod")
                        if y_pred == 1:
                            smell.append("LongMethod")
                        elif (float(res.pc) > 5):
                            smell.append("LongMethod")

                else:
                    if(float(res.lcom) >= 0.4 and float(res.lcom) <= 0.6):
                        y_pred = self.callAlgo(6270,text,"MultiFaceted")
                        if y_pred == 1:
                            smell.append("MultiFaceted")
                        elif (float(res.lcom) > 0.6):
                            smell.append("MultiFaceted")
                        

            #y_pred = self.new_method(count, text, qaulifiedName, className, val)
            print('result')
            print(y_pred)

            return HttpResponse(
                json.dumps({"is_file_uploaded":True,"smell":smell}),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            return Response(
                
                f"[ERR]: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    def callAlgo(self, count, text, smell):

        text = text.replace('\n', ' ').replace('\r', '')
        tokenized_text = self.tokenizer.tokenize(text)
        input_ids = self.tokenizer.convert_tokens_to_ids(tokenized_text)
            #print('idssss')
           
        X_train = numpy.array(input_ids,dtype=float)
        print('1')
        h = X_train.shape[0]
        print('2')
        w = count - h
        print('count'+ str(count))
        print('shape'+str(h))
        if w < 0:
            w = h % count
            X_train = X_train[:count]    
        else:
            X_train = numpy.pad(X_train,(0,w), 'maximum')
        print('new shape'+str(X_train.shape[0]))
        print('3')
        X_train = X_train.reshape(1,count)
        print('4')
        print('Xtrain')
        print(smell)
           # print(X_train)
        if(smell == "ComplexMethod"):
            y = self.autoencoder_cm.predict(X_train)
        elif (smell == "LongMethod"):
            y = self.autoencoder_lp.predict(X_train)
        else:
            y = self.autoencoder_abs.predict(X_train)

        y = y.reshape(y.shape[0], y.shape[1])   
        mse = numpy.mean(numpy.power(X_train - y, 2), axis=1)                            
            #print(mse)
        y_pred = 1 if mse > 400000 else 0 
        return y_pred


class LoadDataFilesViewSet(ViewSet):
    global metrics
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
        listMethods = []
        listClass = []
        for row in method_file_uploaded:
            if line_count_meth == 0:
                line_count_meth += 1
                #print(row)
                continue
            tokens = str(row).split(",")
            mToken = MethodMetric(tokens[0],tokens[1],tokens[2], tokens[3], tokens[4], tokens[5], tokens[6])
            listMethods.append(mToken)
        metrics.setMethodMetrics(listMethods)
        file = open('items.txt','w')
        for entry in listMethods:
           file.write(str(entry.package)+','+str(entry.type)+','+str(entry.method)+','+str(entry.loc)+"\n")
        #print('length'+str(len(listClass))+" and "+str(len(listMethods)))
        file.write('methods done')
        line_count_class = 0
        for row in class_file_uploaded:
            if line_count_class == 0:
                line_count_class += 1
                #print(row)
                continue
            tokens = str(row).split(",")
            cToken = ClassMetric(tokens[0],tokens[1],tokens[2], tokens[11])
            listClass.append(cToken)  
        metrics.setClassMetrics(listClass)
        file = open('items.txt','w')
        for entry in listClass:
           file.write(str(entry.package)+','+str(entry.type)+','+str(entry.LCOM)+"\n")
        print('length'+str(len(listClass))+" and "+str(len(listMethods)))

        return HttpResponse(
                status=status.HTTP_200_OK,
            )
        
class LoadFileViewSet(ViewSet):
    global metrics
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

class LoadRetrainModel(ViewSet):
    
    @swagger_auto_schema()
    def create(self, request):
        x = threading.Thread(target=train_model)
        x.start()
        return HttpResponse(
                status=status.HTTP_200_OK,
            )