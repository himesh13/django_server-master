import numpy
import transformers
import os
from keras.models import load_model
maxLength = 894
def train_model():
    print('In retrain model')
    tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-cased")
    try:
        for smell in ['MultiFaceted','LongMethod','ComplexMethod']:
            X = []
            Y = []
            smellPath = './data/code/'+smell
            final_text = ""
            if(smell == 'ComplexMethod'):
                maxLength = 894
            elif(smell == 'LongMethod'):
                maxLength = 1074
            else:
                maxLength = 6270
                

            for file in os.listdir(smellPath+'/True'):
            #print(os.path.basename(file))
                with open(os.path.join(smellPath+'/True', file),"r",encoding='utf-8') as read_file:
                    try:
                        text = read_file.read()
        #            tokenized_text = tokenizer.tokenize(text,padding = "max_length")
                        tokenized_text = tokenizer.tokenize(text)
        
                        input_ids = tokenizer.convert_tokens_to_ids(tokenized_text)
                        final_text += ' '.join(map(str, input_ids))
                        arr = numpy.fromstring(final_text, dtype=numpy.int64, sep=" ",count=maxLength)
                        print(type(arr))
                        arr_size = len(arr)
                        if arr_size <= maxLength:
                                arr[arr_size:maxLength] = 0
                        if arr_size > maxLength:
                                arr = arr[0:maxLength]
                        X.append(arr)
                        X_np = numpy.array(X)
                        X_np = X_np.reshape(-1,maxLength,1)
                        Y = Y +[1]
                    except Exception as e:
                        print(e)
                        pass
            if(smell == 'ComplexMethod'):
                autoencoder = load_model('lstm_model.h5')
                
            elif(smell == 'LongMethod'):
                autoencoder = load_model('lstm_model_lp.h5')
            else:
                autoencoder = load_model('lstm_model_ma.h5')
                
            print(len(X_np))
            autoencoder.fit(X_np,
                                X_np,
                                epochs=15,
                                batch_size=16,
                                verbose=1,
                                validation_split=0.2,
                                shuffle=True).history
            
            if(False):
                if(smell == 'ComplexMethod'):
                    autoencoder = load_model('lstm_model.h5')
                    autoencoder.save('lstm_model.h5')
                elif(smell == 'LongMethod'):
                    autoencoder = load_model('lstm_model_lp.h5')
                    autoencoder.save('lstm_model_lp.h5')
                else:
                    autoencoder = load_model('lstm_model_ma.h5')
                    autoencoder.save('lstm_model_ma.h5')
                    
    except:
         print('got an exception')


