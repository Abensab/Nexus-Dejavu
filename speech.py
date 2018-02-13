#!/usr/bin/python

from __future__ import print_function
import speech_recognition as sr
import io, base64, sys
from nxsugarpy import *
import pynexus as nxpy
import os

    
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def recognize(task):
    if not isinstance(task.params, dict) or (isinstance(task.params, dict) and 'audio_stream' not in task.params):
        return None, {"code": nxpy.ErrInvalidParams, "message": ""}
	
    sound = base64.b64decode(task.params['audio_stream'])
    with open('file.wav', 'w') as f:
	f.write(sound)
	
    # Dejavu
    #djv.fingerprint_file("file.wav")
    # google
    audio_stream = io.BytesIO(sound)
    audio_frmt   = task.params.get('audio_frmt', 'wav')
    
    
    #r = sr.Rcognizer(language='es-ES', key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
    r=sr.Recognizer()
    r.dynamic_energy_threshold = True
    with sr.WavFile(audio_stream) as source:
        audio = r.record(source)
    
    
    res, err = None, None
    try:
        res = r.recognize_google(audio, language='es-ES', key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw")
        print(res)
    except Exception as ex:
        if str(ex) == 'Speech is unintelligible':
            return [{'text': '', 'confidence': 1.0}], None
        err = {"code": nxpy.ErrUnknownError, "message": ""}
        eprint(ex)

    return res, err
    #Dejavu, cambiar nombre del fichero y fingerprintears
    #djv.fingerprint_file("res.wav")
    
    #os.remove(path...)
if __name__ == '__main__':
    server, err = newServerFromConfig()
    if err:
        raise Exception(err)

    service, err = server.addService('speech')
    if err:
        raise Exception(err)

    service.addMethod('recognize', recognize)
    server.serve()
