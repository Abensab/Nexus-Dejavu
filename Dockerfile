FROM debian:latest

ADD /dejavu_postgres /dejavu_postgres
ADD config.json /config.json 
ADD dejavu.cnf /dejavu.cnf 
ADD speech.py /main.py
RUN apt-get update &&\
    apt-get -y install apt-utils python python-pip python-matplotlib python-tk ffmpeg libasound-dev python-pyaudio &&\
    pip install setuptools 
RUN pip install wheel pynexus nxsugarpy PyMySQL pydub psycopg2 SpeechRecognition matplotlib numpy scipy &&\
    apt-get -y autoremove
RUN apt-get install vi, nano &&\
    apt-get -y autoremove
CMD ["/usr/bin/python", "/main.py"]
