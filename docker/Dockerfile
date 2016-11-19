FROM robinlin/analytic-base

MAINTAINER robin robin890650@gmail.com

ENV PYTHONIOENCODING=utf_8

# install mysql
RUN apt-get update && \
    apt-get install mariadb-server python-mysqldb git vim -y --force-yes
ADD my.cnf /etc/mysql/my.cnf

# install python dep
RUN pip install Django rpy2 djangorestframework==3.4.1 cvxpy numexpr

# install R dep
# install required R packages
RUN echo "options(repos = c(CRAN = 'https://cran.rstudio.com'))" > /root/.Rprofile && \
    R -e 'source("http://bioconductor.org/biocLite.R") ; biocLite(c("graph","RBGL","Rgraphviz"), ask=FALSE) ' && \
    R -e 'install.packages(c("R.oo", "methods", "R.matlab", "data.table", "distr", "entropy", "plyr", "FNN", "e1071", "stringr", "gRim", "gRain", "gRbase", "caret", "rPython", "crayon"))'


WORKDIR /opt
RUN git clone https://github.com/JiaMingLin/de-identification.git && \
    cd de-identification && \
    git fetch && \
    git pull

WORKDIR /opt/de-identification

RUN mkdir log/ && \
    ./clean.sh

# install redis and celery
ADD celery.conf /etc/supervisor/conf.d/celery.conf
RUN apt-get install software-properties-common -y --force-yes && \
    add-apt-repository -y ppa:rwky/redis && \
    apt-get update && \
    apt-get install redis-server supervisor -y && \
    pip install celery redis supervisor && \
    service supervisor restart && \
    supervisorctl reread && \
    supervisorctl update

ADD start.sh /opt/de-identification/start.sh
RUN chmod +x /opt/de-identification/start.sh

VOLUME ["/opt/de-identification/static/test/", "/opt/de-identification/log/"]
#VOLUME ["/opt/de-identification/"]
EXPOSE 8080

ENTRYPOINT /opt/de-identification/start.sh
