# early-fault-detection
Early fault detection during production

## Components
* *data-processing-agent:*
Configuration for [IoT Learning Agent](https://linksmart.eu/redmine/projects/iot-data-processing-agent)
* *plm_connector:*
Connector to [Siemens PLM Software](https://www.plm.automation.siemens.com/en/)
* *pyro-ns:*
[Pyro4 Nameserver](https://pythonhosted.org/Pyro4/nameserver.html) docker image
* *simulation_model:*
PLM Simulation Model files
* *training:*
Machine learning module

## Deployment

### Docker-Compose
```
docker-compose up
```
