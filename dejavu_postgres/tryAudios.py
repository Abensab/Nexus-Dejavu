import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer

# load config from a JSON file (or anything outputting a python dictionary)
with open("dejavu.cnf.SAMPLE") as f:
    config = json.load(f)
    print(config)

if __name__ == '__main__':

	# create a Dejavu instance
	djv = Dejavu(config)

	# Fingerprint all the wav's in the directory we give it
        print('FingerPrinting directory')
        #djv.fingerprint_directory("training-wav", [".wav"])

	djv.fingerprint_file("training-wav/1.wav")
	djv.fingerprint_file("training-wav/2.wav")
	
	# Recognize audio from a file
        print("[Probando con una meloia entrenada]")
        song = djv.recognize(FileRecognizer, "training-wav/1.wav")
        print "From file we recognized: %s\n" % song
        
        print("Probamos los tests...")
        print("[4.wav=3.wav]")
        song = djv.recognize(FileRecognizer, "test-wav/4.wav")
        print "From file we recognized: %s\n" % song
       
        print("[silencio.wav=silencio.wav]")
        song = djv.recognize(FileRecognizer, "test-wav/silencio.wav")
        print "From file we recognized: %s\n" % song

        print("[7.wav=2.wav]")
        song = djv.recognize(FileRecognizer, "test-wav/7.wav")
        print "From file we recognized: %s\n" % song
       
        for i in range(1,10):
            print('-Probando el archivo 7_'+str(i)+".wav")
            song = djv.recognize(FileRecognizer, "test-wav/7_"+str(i)+".wav")
	    print "From file we recognized: %s\n" % song

        print('[Probamos los archivos con desfase]')
        
        for i in range (1,4):
            print('-Probando el archivo 2_'+str(i)+".wav")
            song = djv.recognize(FileRecognizer, "test-wav/2_"+str(i)+".wav")
	    print "From file we recognized: %s\n" % song
	    print (song['song_name'])
	    print (song['confidence'])
	    
        """
        # Or use a recognizer without the shortcut, in anyway you would like
	recognizer = FileRecognizer(djv)
	song = recognizer.recognize_file("test-wav/7.wav")
        print "No shortcut, we recognized: %s\n" % song
        """
