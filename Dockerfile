FROM debian:latest

ADD /dejavu_postgres /dejavu_postgres
ADD config.json /config.json 
ADD dejavu.cnf /dejavu.cnf 
ADD speech.py /main.py
RUN apt-get update &&\
    apt-get -y install locales apt-utils python python-pip python-matplotlib python-tk ffmpeg libasound-dev python-pyaudio &&\
    pip install setuptools 
RUN pip install wheel pynexus nxsugarpy pydub psycopg2 SpeechRecognition matplotlib numpy scipy &&\
    apt-get -y autoremove
RUN locale-gen es_ES.UTF-8
COPY ./default-locale /etc/default/locale
RUN chmod 0755 /etc/default/locale
ENV LANG=es_ES.UTF-8 LANGUAGE=es_ES:es LC_ALL=es_ES.UTF-8
RUN apt-get -y autoremove
CMD ["/usr/bin/python", "/main.py"]
