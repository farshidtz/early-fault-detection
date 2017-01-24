FROM python:2.7-onbuild

#RUN apt-get update
#RUN apt-get install -y netcat net-tools

COPY . /usr/src/app/

ENTRYPOINT ["python", "-u", "pyroAdapter.py"]

EXPOSE 9100
