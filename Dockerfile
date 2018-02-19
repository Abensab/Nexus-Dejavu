FROM debian:latest

ADD /dejavu_postgres /dejavu_postgres 
ADD config.json /config.json
ADD dejavu.cnf.SAMPLE /dejavu.cnf
ADD speech.py /main.py
RUN apt-get update
RUN apt-get -y install apt-utils
RUN apt-get -y install python python-pip python-matplotlib ffmpeg libasound-dev python-pyaudio
RUN pip install wheel pynexus nxsugarpy PyMySQL pydub psycopg2 SpeechRecognition matplotlib numpy scipy
CMD ["/usr/bin/python", "/main.py"]
