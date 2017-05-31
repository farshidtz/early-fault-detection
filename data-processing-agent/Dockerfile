FROM java:openjdk-8-jre

COPY *.jar /usr/src/app/
WORKDIR /usr/src/app

#ENV CLASSPATH .:./lib/ceml-1.4.0-SNAPSHOT.jar

ENV env_var_enabled=true
ENV cep_init_engines=eu.linksmart.services.event.cep.engines.EsperEngine
ENV agent_init_extensions=eu.linksmart.services.event.ceml.core.CEML

ENTRYPOINT ["java", "-jar", "iot.learning.universal.agent-1.5.0-20170531.113430-5.jar"]

VOLUME /config
EXPOSE 8319
