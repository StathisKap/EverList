import time
import os
import base64
import random
import uuid
import urllib
import collections
import urllib.parse
import hmac
import hashlib
import binascii
import requests
import webbrowser 
import urllib.parse as urlparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

def escape(s):
    return urllib.parse.quote(s, safe='~')
def get_nonce():
    return uuid.uuid4().hex

def stringify_parameters(parameters):
    output = ''
    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))

    counter = 1
    for k, v in ordered_parameters.items():
        output += escape(str(k)) + '=' + escape(str(v))
        if counter < len(ordered_parameters):
           output += '&'
           counter += 1

    return output
oauth_parameters={
'oauth_timestamp': str(int(time.time())),
'oauth_signature_method': "HMAC-SHA1",
'oauth_version': "1.0",
'oauth_nonce': get_nonce(),
'oauth_consumer_key': 'stathiskap75',
'oauth_callback':'http:127.0.0.1:8000'
}

string_parameters=stringify_parameters(oauth_parameters)
secret='b6c95bdf98d5953f'

key = (escape(secret)+'&').encode()
message = ('GET&' + escape('https://sandbox.evernote.com/oauth') + '&' + escape(string_parameters)).encode()
signature = hmac.new(key, message, hashlib.sha1).digest()
oauth_parameters['oauth_signature'] = base64.b64encode(signature).decode()

res = requests.get('https://sandbox.evernote.com/oauth?' + stringify_parameters(oauth_parameters))

print(res.status_code)
print(res.text)
print()
auth_token = res.text[:res.text.find("&")]
webbrowser.open("https://sandbox.evernote.com/OAuth.action" + "?" + auth_token)

httpd = HTTPServer(('127.0.0.1', 8000), SimpleHTTPRequestHandler)
httpd.handle_request()

# https://sandbox.evernote.com/oauth?
#   oauth_consumer_key=internal-dev -- DONE in oauth_parameters
#   &auth_token=internaldev.14CD91FCE1F.687474703A2F2F6C6F63616C686F7374.6E287AD298969B6F8C0B4B1D67BCAB1D -- DONE in auth_token
#   &oauth_verifier=40793F8BAE15D4E3B6DD5CA8AB4BF62F -- NOT DONE
#   &oauth_nonce=4078121641140961292 -- DONE in oauth_parameters
#   &auth_signature=hfA8r3NdMnZbzN0OOmTZIZj6Wkc= -- NOT DONE in oauth_parameters
#   &oauth_signature_method=HMAC-SHA1 -- DONE in oauth_parameters
#   &oauth_timestamp=1429572048 -- DONE in oauth_parameters
#   &oauth_version=1.0 -- DONE in oauth_parameters