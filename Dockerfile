FROM python

WORKDIR /Youtube
COPY . /Youtube

RUN pip install -r requirements.txt

CMD python3 tg_tube.py