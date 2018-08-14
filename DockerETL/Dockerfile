FROM python:3.6.3

USER root

# Consolidate install requirements
COPY requirements.txt /tmp
RUN apt-get update && \
    apt-get -qy --force-yes install --reinstall build-essential && \
    apt-get -qy --force-yes install gcc freetds-dev freetds-bin unixodbc-dev tdsodbc && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Add dedupe scripts (local clone, not pulling from latest - should it be that way?)
# build the pyx files, run unit tests
# verify that we can continue with docker image build
ADD dedupe /dedupe
RUN /bin/bash /dedupe/build_me.sh

# Configure ODBC
COPY odbcinst.ini /etc/odbcinst.ini
RUN odbcinst -q -d -i -f /etc/odbcinst.ini

CMD ["python"]
