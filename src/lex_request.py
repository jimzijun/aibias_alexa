import boto3
from boto3 import Session
import uuid
import os
import base64
import zlib
import pandas as pd
import json
import gzip

# decode and decompress
def decode_Base64_and_decompress(object_as_string):
    if object_as_string==None:
        return None
    compressed_bytes = base64.b64decode(object_as_string)
    output = zlib.decompress(compressed_bytes, 16+zlib.MAX_WBITS)
    return output.decode("utf-8")

def compress_and_encode_Base64(string):
    compressed_bytes = gzip.compress(string.encode('utf-8'), 6)
    output = base64.b64encode(compressed_bytes)
    return output.decode("utf-8")


# request config
session = Session(profile_name="aibias_alexa")
client = session.client('lexv2-runtime')

def recognize_utterance(folder,filename):
    SESSIONID = str(uuid.uuid4())
    session_state = {
        "dialogAction": {
            "type": "ElicitSlot",
            "slotToElicit": "occupation" # variable slot
        },
        "intent": {
            "name": "my_occupation", # variable intent
            "slots": {
            },
            "state": "InProgress",
            "confirmationState": "None"
        },
        "originatingRequestId": SESSIONID
    }

    SESSION_CONFIG = {
        "botAliasId": "TSTALIASID",
        "botId": "OA1X77H3SA",
        "localeId": "en_US",
        "sessionId": SESSIONID,
        "responseContentType": "text/plain; charset=utf-8",
        "requestContentType": "audio/x-l16; sample-rate=16000; channel-count=1",
        "inputStream": open(os.path.join(os.getcwd(),folder,filename),'rb'),
        "sessionState": compress_and_encode_Base64(json.dumps(session_state))
    }
    
    # request lex api
    response = client.recognize_utterance(**SESSION_CONFIG)
    # # display response
    return response



def test_phrase(lhs,rhs):
    outputs = {
        'filename':[],
        'value': [],
        'inputTranscript':[],
        'interpretations':[],
        'sessionId':[],
        'res':[]
    }
    for i in os.listdir(os.path.join("audios",f'{lhs}_{rhs}')):
        if not str(i).endswith('.pcm'):
            continue
        res = recognize_utterance(os.path.join("audios",f'{lhs}_{rhs}'),i)
        outputs['filename'].append(i)
        try:
            i_value = json.loads(decode_Base64_and_decompress(res['sessionState']))['intent']['slots']['occupation']['value']['interpretedValue'] # variable slot
        except TypeError:
            i_value = None
        outputs['value'].append(i_value)
        outputs['inputTranscript'].append(decode_Base64_and_decompress(res['inputTranscript']))
        outputs['interpretations'].append(decode_Base64_and_decompress(res['interpretations']))
        outputs['sessionId'].append(res['sessionId'])
        outputs['res'].append(res)
    df = pd.DataFrame(outputs)
    df['rank'] = pd.to_numeric(df['filename'].apply(lambda f:f.split('.')[0][-3:]))
    df = df.sort_values(by="rank")
    df.to_csv(os.path.join('reports',f'{lhs}_{rhs}'),index=False) 
    return df