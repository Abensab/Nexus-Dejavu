#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys, os, shutil, random , warnings,io, base64, json
import pynexus as nxpy
import speech_recognition as sr
#warnings.filterwarnings("ignore")
sys.path
sys.path.append(os.getcwd()+'/dejavu_postgres/')
from nxsugarpy import *
from dejavu import Dejavu
from dejavu import fingerprint
import dejavu.decoder as decoder
from dejavu.recognize import FileRecognizer
import threading

lock = threading.Lock()
invalid_params = 0
void_sound = 0
dejavu_recognized = 0
google_recognized = 0
no_recognized_word = 0 
  
with open("dejavu.cnf") as f:
    config = json.load(f)  
    
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def stats(task):
    global service
    global invalid_params
    global void_sound
    global dejavu_recognized
    global google_recognized
    global no_recognized_word
    try:
        del task.params['audio_stream']
    except:
	pass
    service.logWithFields(InfoLevel, {"type": "pull", "path": task.path, "method": task.method, "params": task.params, "tags": task.tags}, "task[ path={0} method={1} params={2} tags={3} ]", task.path, task.method, task.params, task.tags)
    with lock:
        res = {
            'InvalidParams': invalid_params,
            'VoidSound':void_sound,
            'DejavuRecognized':dejavu_recognized,
            'GoogleRecognized':google_recognized,
            'NoRecognizedWord':no_recognized_word
        }
    return res, None

def recognize(task):
    global service
    global invalid_params
    global void_sound
    global dejavu_recognized
    global google_recognized
    global no_recognized_word
    
    if not isinstance(task.params, dict) or (isinstance(task.params, dict) and 'audio_stream' not in task.params):
        with lock: invalid_params += 1
        service.logWithFields(InfoLevel, {"type": "pull", "path": task.path, "method": task.method, "params": task.params, "tags": task.tags}, "task[ path={0} method={1} params={2} tags={3} ]", task.path, task.method, task.params, task.tags)
        return None, {"code": nxpy.ErrInvalidParams, "message": ""}
    
    res = [{'text': ' ', 'confidence': 1.0}]
    err = None
    
    sound = base64.b64decode(task.params['audio_stream'])
    name_file= 'grabaciones/file'+str(random.randint(0, 10000))+'.wav'
    
    try:
        del task.params['audio_stream']
    except:
	pass
	
    service.logWithFields(InfoLevel, {"type": "pull", "path": task.path, "method": task.method, "params": task.params, "tags": task.tags}, "task[ path={0} method={1} params={2} tags={3} ]", task.path, task.method, task.params, task.tags)
    
    
    
    with open(name_file, 'w') as f:
	f.write(sound)
    
    if is_silent(name_file):
	os.remove(name_file)
        with lock: void_sound+=1
	return res, err
						    
    # Dejavu
    song = djv.recognize(FileRecognizer,name_file)
    if song!=None and song['confidence']>100:
	os.remove(name_file)
        with lock: dejavu_recognized +=1
	res[0]['text']=song['song_name']
	
    else:	
    
	audio_stream = io.BytesIO(sound)
	audio_frmt   = task.params.get('audio_frmt', 'wav')
   
	r=sr.Recognizer()
	r.dynamic_energy_threshold = True
    
	try:
	    with sr.AudioFile(audio_stream) as source:
		audio = r.record(source)
	    g_res = r.recognize_google(audio, language='es-ES', key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
	    if g_res!=None:
		#Dejavu, cambiar nombre del fichero y fingerprintear
		print("aqui se supone que da el error: ")
		path="grabaciones/"+g_res.encode("utf8")+".wav"
		print(repr(g_res))
		print(repr(g_res.encode("utf8")))
		print(repr(path))
		print(repr(path.encode("utf8")))
		fingerprint_file(name_file, path)
		res[0]['text']=g_res
                with lock: google_recognized +=1
	    else:
                with lock: no_recognized_word +=1
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
	    
            with lock: no_recognized_word +=1
	    return res, err
	    

    return res, err


def fingerprint_file(name_file, new_path):  
    print(repr('fingerprinting...'))
    shutil.move(name_file, new_path)
    djv.fingerprint_file(new_path)
    print(repr('...fingerprinted'))
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
    try:
        server, err = newServerFromConfig()
    
	if err:
	    raise Exception(err)
	methodOpts={ 'disablePullLog':True, 'enableResponseResultLog':True, 'enableResponseErrorLog':True}
	service, err = server.addService('speech')
	if err:
	    raise Exception(err)
   
	try:
	    os.makedirs('grabaciones/')
	except OSError:
	    pass
	djv = Dejavu(config)
	service.addMethod('recognize', recognize, methodOpts = methodOpts)
	service.addMethod('stats', stats, methodOpts = methodOpts)
	server.serve()
    except (KeyboardInterrupt):
        raise
    
