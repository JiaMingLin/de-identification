FROM robinlin/analysis-base
MAINTAINER robin robin890650@gmail.com

# install python dep
RUN apt-get update && \
	apt-get dist-upgrade -y --force-yes && \
	apt-get install git python-numpy python-scipy python-pandas python-pip libatlas-base-dev gfortran python-dev -y --force-yes && \
	pip install cvxpy rpy2

# install required R packages
RUN echo "options(repos = c(CRAN = 'https://cran.rstudio.com'))" > /root/.Rprofile && \
	R -e 'source("http://bioconductor.org/biocLite.R") ; biocLite(c("graph","RBGL","Rgraphviz"), ask=FALSE) ' && \
	R -e 'install.packages(c("R.oo", "methods", "R.matlab", "data.table", "distr", "entropy", "plyr", "FNN", "e1071", "stringr", "gRim", "gRain", "gRbase", "caret", "rPython", "crayon"))'

RUN git clone https://github.com/JiaMingLin/de-identification.git

WORKDIR /de-identification

VOLUME ['/de-identification/static/test/', '/de-identification/log']