FROM python:2.7-alpine

RUN pip install --no-cache-dir paho-mqtt

WORKDIR /home

COPY *.py /home/

VOLUME /config

ENTRYPOINT ["python", "-u", "plm_connector.py"]
CMD ["-c", "/config/config.json"]
