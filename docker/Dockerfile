FROM robinlin/analytic-base

MAINTAINER robin robin890650@gmail.com

# install mysql
RUN apt-get update && \
    apt-get install mariadb-server python-mysqldb git -y --force-yes
ADD my.cnf /etc/mysql/my.cnf

# install python dep
RUN pip install Django rpy2 djangorestframework cvxpy

# install R dep
# install required R packages
RUN  R -e 'install.packages(c("R.oo", "methods", "R.matlab", "data.table", "distr", "entropy", "plyr", "FNN", "e1071", "stringr", "gRim", "gRain", "gRbase", "caret", "rPython", "crayon"))'

WORKDIR /opt
RUN git clone https://github.com/JiaMingLin/de-identification.git && \
    cd de-identification && \
    git fetch && \
    git pull

WORKDIR /opt/de-identification

RUN mkdir log/ && \
    ./clean.sh

ADD start.sh /opt/de-identification/start.sh
RUN chmod +x /opt/de-identification/start.sh

VOLUME ["/opt/de-identification/static/test/", "/opt/de-identification/log/"]
EXPOSE 8080

ENTRYPOINT /opt/de-identification/start.sh