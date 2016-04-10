from rtlsdr import RtlSdr
from gnuradio import blocks
import argparse
import requests
import json
from optparse import OptionParser
from gnuradio.eng_option import eng_option
import math
import numpy

def get_available_whitespace(lat, lon,apiKey):
	req = {}
	req["jsonrpc"] = "2.0"
	req["method"] = "spectrum.paws.getSpectrum"
	req["apiVersion"] = "v1explorer"
	params = {}
	params["type"] = "AVAIL_SPECTRUM_REQ"
	params["version"] = "1.0"
	params["deviceDesc"] = { "serialNumber": "124", "fccId": "TEST", "fccTvbdDeviceType": "MODE_1" }
	params["location"] = { "point": { "center": {"latitude": lat, "longitude": lon} } }
	params["antenna"] = { "height": 30.0, "heightType": "AGL" }
	params["owner"] = { "owner": { } }
	params["capabilities"] = { "frequencyRanges": [{ "startHz": 800000000, "stopHz": 850000000 }, { "startHz": 900000000, "stopHz": 950000000 }] }
	params["key"] = apiKey
	req["params"] = params
	req["id"] = "any_string"
	r  = json.dumps(req)
	request = json.loads(r)
	print json.dumps(request,indent=4)
	r = requests.post( "https://www.googleapis.com/rpc", headers={"Content-Type":"application/json"}, data = json.dumps(request))
	resp = r.json()
	print json.dumps(resp,indent=4)
	return resp["result"]["spectrumSchedules"][0]
	
 

def parse_options():
     parser = OptionParser(option_class=eng_option, usage="python rtlsdr-tv-whitspace-sensor.py --lat lat --lon lon")
     parser.add_option( "--lat", type="eng_float", default=None, help = "Latitude")
     parser.add_option("--lon",  type="eng_float", default=None, help = "Longitude")
     parser.add_option("--samp-rate","-s", type="eng_float", default = 1e6, help="Sample rate")
     parser.add_option("--dwell-time","-d", type="eng_float", default = 0.5, help="Samples in each bin")
     parser.add_option("--required-bw", "-r", type = "eng_float", default = 5e6, help="Required spectrum")
     parser.add_option("--threshold", "-t", type = "eng_float", default = 0, help="power threshold for occupancy")
     parser.add_option("--api-key", "-k", type = "string", default = 0, help="Required google API key for tv whitespace")
     options,args = parser.parse_args()
     return options


def find_spectrum_hole(whitespace, requiredSpectrum, threshold):
     spectra = whitespace ["spectra"][0]['frequencyRanges']
     print "Spectrum :", str(spectra)
     # Find hole with max power 
     maxPowerDBm = threshold 
     foundSpectrum = None
     for spectrum in spectra:
	if spectrum["maxPowerDBm"] > maxPowerDBm \
	    and (spectrum["stopHz"] - spectrum["startHz"]) >= requiredSpectrum:
	    maxPowerDBm = spectrum["maxPowerDBm"]
	    foundSpectrum = spectrum
     return foundSpectrum
	   
	

if __name__ == '__main__':
     options = parse_options()

     whitespace = get_available_whitespace(options.lat,options.lon,options.api_key)
     spectrumHole = find_spectrum_hole(whitespace,options.required_bw,options.threshold)
     startHz = spectrumHole["startHz"]
     stopHz = spectrumHole["stopHz"]
     print "Found Spectrum Hole - startHz = ", startHz, " stopHz = ", stopHz

     offset = options.samp_rate/2
     hopCount = options.required_bw/options.samp_rate

     if hopCount == 0:
	hopCount = 1

     sampleCount = options.dwell_time*options.samp_rate
	
     p = int(math.log(sampleCount,2) + 1)
	
     sampleCount = pow(2,p)
	
     print "SampleCount ", sampleCount
   
     sdr = RtlSdr()
     sdr.sample_rate = options.samp_rate
     sdr.gain = 4
     sdr.freq_correction = 60

     while True:
         for i in range(0,int(hopCount) - 1):
	     sdr.center_freq = startHz + i*options.samp_rate + offset
	     samples = sdr.read_samples(sampleCount)
	     energy = numpy.linalg.norm(samples)/sampleCount
	     print "Center Freq ", (startHz + i*options.samp_rate + offset)/1e6 , " Mhz", " Energy ", energy


     
    
     


