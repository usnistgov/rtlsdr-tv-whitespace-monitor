# rtlsdr-tv-whitespace-monitor

This script consults the Google TV whitespace databse, finds an available 
hole that is bigger than the requested bandwidth and monitors that
hole.

## Instructions:

This script uses python 2.7

1. Get an API_KEY from Google for access to the google TV whitespace database. This is free for research use.

2. Install python packages: requests, numpy and pyrtlsdr using pip install

3. Run :

      python sense-whitespace.py --lat 39.086768 --lon -77.179863 --api-key "API_KEY"

