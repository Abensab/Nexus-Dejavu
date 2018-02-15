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
from dejavu import fingerprint
import dejavu.decoder as decoder
from dejavu.recognize import FileRecognizer
  
with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)  
    
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def recognize(task):
    res = [{'text': ' ', 'confidence': 1.0}]
    err = None

    
    if not isinstance(task.params, dict) or (isinstance(task.params, dict) and 'audio_stream' not in task.params):
        return None, {"code": nxpy.ErrInvalidParams, "message": ""}
    
    sound = base64.b64decode(task.params['audio_stream'])
    name_file= 'grabaciones/file'+str(random.randint(0, 10000))+'.wav'
    
    with open(name_file, 'w') as f:
	f.write(sound)
    
    if is_silent(name_file):
	os.remove(name_file)
	return res, err
						    
    # Dejavu
    song = djv.recognize(FileRecognizer,name_file)
    if song!=None and song['confidence']>100:
	print('--Reconocida, confidence: '+str(song['confidence']))
	os.remove(name_file)
	print(song['song_name'])
	res[0]['text']=song['song_name']
	
    else:	
        print('--No reconocida en Dejavu---')
    
	audio_stream = io.BytesIO(sound)
	audio_frmt   = task.params.get('audio_frmt', 'wav')
   
	r=sr.Recognizer()
	r.dynamic_energy_threshold = True
    
	try:
	    with sr.AudioFile(audio_stream) as source:
		audio = r.record(source)
	    print('Antes de google')
	    g_res = r.recognize_google(audio, language='es-ES', key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
	    print('Despues de google')
	    if g_res!=None:
		print("--Google:"+g_res)
		#Dejavu, cambiar nombre del fichero y fingerprintear
		fingerprint_file(name_file, 'grabaciones/'+g_res+'.wav')
		res[0]['text']=g_res;
	    else:
		print('Error en Google: '+ g_res)
	except Exception as ex:
	    
	    eprint(ex)
	    if str(ex) == '':
		print('--UnknownValueError')
		#UnknownValueError twrhowed by r.recognize_google(), like silences or some noise audios
		fingerprint_file(name_file, 'grabaciones/ .wav')
		
	    if str(ex) == 'Audio file could not be read as PCM WAV, AIFF/AIFF-C, or Native FLAC; check if file is corrupted or in another format':
		#NO Entrenar en Dejavu el no legible porque Google no ha detectado 
		err = {"code": nxpy.ErrUnknownError, "message": ""}
		
	    elif str(ex) == 'Speech is unintelligible':
		print('--Speech is unintelligible')
		#Entrenar en Dejavu el no legible para que no pase por google
	        fingerprint_file(name_file, 'grabaciones/ .wav')
	    
	    return res, err
	    

    return res, err


def fingerprint_file(name_file,new_path):
    shutil.move(name_file, new_path)
    djv.fingerprint_file(new_path)
    os.remove(new_path)


def is_silent(file_path): 
    hashes = get_fingerprints(file_path,None,None)
    if(len(hashes)==0):
       return True
    return False


def get_fingerprints(file_path, limit=None, song_name=None):
    #Fingerprints a file and send the number of fingerprints that found
    try:
        filename, limit = file_path
    except ValueError:
        pass

    songname, extension = os.path.splitext(os.path.basename(file_path))
    song_name = song_name or songname
    channels, Fs = decoder.read(file_path, limit)
    result = set()
    channel_amount = len(channels)
    
    for channeln, channel in enumerate(channels):
        hashes = fingerprint.fingerprint(channel, Fs=Fs)     
        result |= set(hashes)
	
    return result


   
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
