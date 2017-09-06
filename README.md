# de-identification
This project is an implementation of 
* [Differentially Private High-Dimensional Data Publication via Sampling-Based Inference](http://dl.acm.org/citation.cfm?id=2783379)
* [PriView: practical differentially private release of marginal contingency tables](http://dl.acm.org/citation.cfm?id=2588575&CFID=807218332&CFTOKEN=75481269)

## Installation
The Docker image is now available on Docker Hub.

Using the following commands to launch the application.
<pre>docker run -itd \ 
     -p HOST_PORT:8080 \ 
     -v USER_DATA:/opt/de-identification/static/test/ \
     -v USER_LOG:/opt/de-identification/log/ \ 
     robinlin/de-identification \
     /bin/bash</pre>
where
  * **HOST_PORT**: The port available on your machine, e.g. 8080 or 8888
  * **USER_DATA**: The path you place your sensitive data, so that the application can read from.
  * **USER_LOG**: The path you could find the execution log.
Be sure to substitute **HOST_PORT**, **USER_DATA** and **USER_LOG** with your own settings.

## Next Step
See [here](/documents/user_guide.md) a quick start.
