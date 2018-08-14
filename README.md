# dedupPostgresDocker

This is an experimental/learning project to explore using the Python
[dedupe](http://dedupe.readthedocs.org) library with PostgreSQL as well as other [examples](https://github.com/dedupeio/dedupe-examples) from dedupe.io.  
It is not directly intended for general use but allows for a docker-compose environment to be created that includes four docker container builds.

1) DockerETL (Python 3 including the installation of the Dedupe module)

The ```pgdedupe.py``` script borrows heavily from the
[pgsql_big_dedupe_example.py](http://datamade.github.io/dedupe-examples/docs/pgsql_big_dedupe_example.html)
example script with some modifications.  It has been debugged on a
sample set of OSHA inspection records, a fixture for which is
provided.  This data comes from the [OSHA Data
Enforcement](http://enforcedata.dol.gov/views/data_summary.php) set
from the U.S. Department of Labor.  It focuses on a subset of the
columns available in the ```osha_inspection``` file.


## installation and use

This script was developed on OS X 10.11.3 using Python 3.5 with the
sample data, then invoked on an EC2 Ubuntu 14.04 machine.  In both
environments, you might want to have Anaconda installed as well as
the gcc and g++ system packages to successfully install the dedupe
library without heavy lifting.

## access postgres adminer

`http://localhost:8080`

## access dedupe.io documentation

https://docs.dedupe.io/en/latest/

## postgres_example.py html with script comments

http://dedupeio.github.io/dedupe-examples/docs/pgsql_example.html
