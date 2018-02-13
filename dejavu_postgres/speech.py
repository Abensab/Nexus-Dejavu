#!/usr/bin/python

from __future__ import print_function
import speech_recognition as sr
import io, base64, sys
from nxsugarpy import *
import pynexus as nxpy
import os
import shutil
import random
import warnings
import json
#warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
  
with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)  
    
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def recognize(task):
    res, err = None, None
    if not isinstance(task.params, dict) or (isinstance(task.params, dict) and 'audio_stream' not in task.params):
        return None, {"code": nxpy.ErrInvalidParams, "message": ""}
	
    sound = base64.b64decode(task.params['audio_stream'])
    name_file= 'grabaciones/file'+str(random.randint(0, 10000))+'.wav'
    
    with open(name_file, 'w') as f:
	f.write(sound)
	
    # Dejavu
    song = djv.recognize(FileRecognizer,name_file)
    if song!=None:
	eprint('--confidence: '+str(song['confidence']))
	if song['confidence']>100:
		os.remove(name_file)
		print(song)
		return song['song_name'], err
		
    

    audio_stream = io.BytesIO(sound)
    audio_frmt   = task.params.get('audio_frmt', 'wav')
   
    r=sr.Recognizer()
    r.dynamic_energy_threshold = True
    with sr.WavFile(audio_stream) as source:
        audio = r.record(source)
    
    
    
    try:
        res = r.recognize_google(audio, language='es-ES', key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
        print(res)
    except Exception as ex:
        if str(ex) == 'Speech is unintelligible':
            return [{'text': '', 'confidence': 1.0}], None
        err = {"code": nxpy.ErrUnknownError, "message": ""}
        eprint(ex)

    
    #Dejavu, cambiar nombre del fichero y fingerprintear
    shutil.move(name_file, 'grabaciones/'+res+'.wav')
    djv.fingerprint_file('grabaciones/'+res+'.wav')
    
    os.remove('grabaciones/'+res+'.wav')
	
    return res, err
    
if __name__ == '__main__':
    server, err = newServerFromConfig()
    if err:
        raise Exception(err)

    service, err = server.addService('speech')
    if err:
        raise Exception(err)
   
    try:
	os.makedirs('grabaciones/')
    except OSError:
	pass
    djv = Dejavu(config)
    service.addMethod('recognize', recognize)
    server.serve()
