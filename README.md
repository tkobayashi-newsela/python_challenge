
# Python Challenge

This is the answer to the python challenge described in the Python Challenge.pdf.
The main goal of this project is to collect a list of ip's in a file and get geoip and rdap information
from each of the ip's.

## Installation

To run this project, it's necessary to have `Docker` and `Docker Compose` installed.

To install the dependencies, it's highly recommended to use python virtual env.

```
virtualenv -p python3 .venv
```

Next, just run:

```
pip install -r requirements.txt
```

## Usage

To interact with the python script, we are going to use invoke.


To process the file and get the geoip and rdap information:
```
invoke run
```

To detroy the enviroment
```
invoke destroy
```


To export the data into a csv file
```
invoke export-to-csv
```

## Caching

To obtain the caching functionality, we use mongodb to store processed information. So before processing any ip, we check if that ip was already processed.
