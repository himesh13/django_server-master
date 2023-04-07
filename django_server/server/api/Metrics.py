import threading
from django_server.server.api.EncoderModel import train_model

class Metrics:
    def __init__(self,classMetrics, methodMetrics):
        self.classMetrics = classMetrics
        self.methodMetrics = methodMetrics
        self.feedbackCount = -1
    
    def getClassMetrics(self):
        return self.classMetrics
    
    def methodMetrics(self):
        return self.methodMetrics
    
    def setMethodMetrics(self,methodMetrics):
        self.methodMetrics = methodMetrics
    
    def setClassMetrics(self,classMetrics):
        self.classMetrics = classMetrics
    
    def doesExistClass(self, packageName, className):
        filtered = [x for x in self.classMetrics if x.package == packageName and x.type == className ]
        if(len(filtered) > 0):
            return True, filtered
        else:
            return False, []
        
    def handleFeedbackCount(self):
        if self.feedbackCount == -1:
            with open("./data/var") as f:
                var = [line.rstrip() for line in f]
                print(var)
            
            if var:
                if int(var[0]) > 1:
                    self.retrainModel()
            
    # def thread_function(name):
    #     print('thread function')

        
    def retrainModel(self):
        print('Retraining model')
        x = threading.Thread(target=train_model)
        x.start()

    def doesExistMethod(self, packageName, className, methodName):
        print("In method collec")
        print(len(self.methodMetrics))
        print(packageName)
        print(className)
        print(methodName)
        filtered = [x for x in self.methodMetrics if x.package == packageName and x.type == className and x.method == methodName ]
        if(len(filtered) > 0):
            return True, filtered
        else:
            return False, []