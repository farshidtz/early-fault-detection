FROM python:2.7-onbuild

COPY pyroAdapter.py /usr/src/app
COPY agent /usr/src/app/agent

ENTRYPOINT ["python", "-u", "pyroAdapter.py"]

VOLUME /data
EXPOSE 9100
