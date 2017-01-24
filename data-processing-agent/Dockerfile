FROM java:8-jdk

COPY . /usr/src/app/
WORKDIR /usr/src/app

ENV CLASSPATH .:./lib/ceml-1.4.0-SNAPSHOT.jar

ENTRYPOINT ["java", "-jar", "iot.learning.rest.agent-1.4.0-SNAPSHOT.jar"]

EXPOSE 8319