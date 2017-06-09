FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
COPY pyroAdapter.py /usr/src/app
COPY manager.sh /usr/src/app
COPY agent /usr/src/app/agent
RUN pip install --no-cache-dir -r requirements.txt

#ENTRYPOINT ["python", "-u", "pyroAdapter.py"]
ENTRYPOINT ["sh", "manager.sh"]

VOLUME /model
# Port range: 9100+{1..CMD}
EXPOSE 9101-9106
