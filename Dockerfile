FROM python

WORKDIR /Youtube
COPY . /Youtube

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install software-properties-common -y
# RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get dist-upgrade
RUN apt-get install -y ffmpeg

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN ffdl install --add-path

# Замените строку в файле
# RUN sed -i 's/var_regex = re.compile(r"^\\w+\\W")/var_regex = re.compile(r"^\\$*\\w+\\W")/g' /usr/local/lib/python3.11/site-packages/pytube/cipher.py


CMD python3 main.py
