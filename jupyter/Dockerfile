FROM jupyter/datascience-notebook

RUN python --version

USER root

RUN conda install --quiet --yes -c conda-forge osmnx dask

RUN conda install --yes --name root spacy pymongo

RUN ["bash", "-c", "source activate root"]

RUN python -m spacy download en

# RUN apt-get update && apt-get -qy install unixodbc-dev

RUN apt-get update && \
    apt-get -qy install --reinstall build-essential && \
    apt-get -qy install gcc freetds-dev freetds-bin unixodbc-dev tdsodbc

RUN pip install --upgrade pip && \
    pip install pyodbc pymysql unidecode dj_database_url

ADD odbcinst.ini /etc/odbcinst.ini
RUN odbcinst -q -d -i -f /etc/odbcinst.ini


RUN pip install -U geopandas \
                   geopy \
                   rtree \
                   folium \
                   numpy \
                   shapely \
                   fiona \
                   six \
                   pyproj \
                   numexpr==2.6.4 \
                   elasticsearch \
                   geojson \
                   plotly \
                   tqdm \
                   mapboxgl \
                   cufflinks \
                   geohash2 \
                   tables \
                   mixpanel \
                   SQLAlchemy \
                   GeoAlchemy2 \
                   twitter \
                   pyodbc

# USER jovyan
USER root

ADD fonts /usr/share/fonts/truetype/

RUN fc-cache
RUN fc-list

VOLUME /notebooks
WORKDIR /notebooks
CMD jupyter notebook --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token='demo'
