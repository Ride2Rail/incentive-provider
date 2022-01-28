FROM python:3.8

WORKDIR /code

ENV FLASK_APP=incentive_provider_api.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY codes codes
COPY incentive_provider_api.py incentive_provider_api.py
COPY incentive_provider_api.conf incentive_provider_api.conf

EXPOSE 5011

CMD ["flask", "run"]
