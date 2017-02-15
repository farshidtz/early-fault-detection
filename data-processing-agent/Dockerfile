FROM java:openjdk-8-jre

COPY iot.learning.agent-1.4.0-SNAPSHOT-jar-with-dependencies.jar /usr/src/app/
WORKDIR /usr/src/app

ENV CLASSPATH .:./lib/ceml-1.4.0-SNAPSHOT.jar

ENTRYPOINT ["java", "-jar", "iot.learning.agent-1.4.0-SNAPSHOT-jar-with-dependencies.jar"]

RUN ln -s /config/conf.cfg ./conf.cfg

VOLUME /config
EXPOSE 8319
