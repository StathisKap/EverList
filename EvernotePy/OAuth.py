import time
import os
import base64
import random
import uuid
import urllib
import collections
import hmac
import hashlib
import binascii
import requests
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
import socketserver
import urllib.parse
from urllib.parse import parse_qs
import cgi
from secrets import dev_secret # This is my developer token in a differnt file named secrets


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
secret = dev_secret

key = (escape(secret)+'&').encode()
message = ('GET&' + escape('https://sandbox.evernote.com/oauth') + '&' + escape(string_parameters)).encode()
print()
print(message)
print()
signature = hmac.new(key, message, hashlib.sha1).digest()
oauth_parameters['oauth_signature'] = base64.b64encode(signature).decode()
print(signature)
print()
for k,v in oauth_parameters.items():
    print(k,v)
print()

res = requests.get('https://sandbox.evernote.com/oauth?' + stringify_parameters(oauth_parameters))
oauth_parametersclone = oauth_parameters

print(res.status_code)
print(res.text)
auth_token = res.text[:res.text.find("&")]
webbrowser.open("https://sandbox.evernote.com/OAuth.action" + "?" + auth_token)
oauth_parameters['oauth_token'] = auth_token[auth_token.find('=') + 1:] 

class MyRequestHandler(BaseHTTPRequestHandler):
    request = ""
    def do_GET(self):
        # print(self.path)
        MyRequestHandler.request = self.path
    def do_POST(self):
        self.send_response(200)
        content_length = int(self.headers.get('Content-Length'))
        print(self.rfile.read(content_length))

httpd = HTTPServer(('127.0.0.1', 8000), MyRequestHandler)
httpd.handle_request()
if not MyRequestHandler.request:
    exit(1)
MRH_Request = MyRequestHandler.request
oauth_verifier = MyRequestHandler.request[MRH_Request.find("oauth_verifier"):MRH_Request.find("&sandbox")]
verifier = oauth_verifier[oauth_verifier.find("=")+1:]
oauth_parameters['oauth_verifier'] = verifier
# oauth_parameters['oauth_signature'] = base64.b64encode(signature).decode()
oauth_parameters.pop('oauth_callback')
oauth_parameters.pop('oauth_signature')
oauth_parameters['oauth_timestamp'] = str(int(time.time()))

# oauth_parameters.pop('oauth_signature')
# message = ('GET&' + escape('https://sandbox.evernote.com/oauth') + '&' + escape(string_parameters)).encode()
# signature = hmac.new(key, message, hashlib.sha1).digest()
# oauth_parameters['oauth_signature'] = base64.b64encode(signature).decode()

string_parameters=stringify_parameters(oauth_parameters)
message = ('GET&' + escape('https://sandbox.evernote.com/oauth') + '&' + escape(string_parameters)).encode()
signature = hmac.new(key, message, hashlib.sha1).digest()
oauth_parameters['oauth_signature'] = base64.b64encode(signature).decode()
print()
print()
print('https://sandbox.evernote.com/oauth?' + stringify_parameters(oauth_parameters))

for k,v in oauth_parametersclone.items():
    print(k,v)

res = requests.get('https://sandbox.evernote.com/oauth?' + stringify_parameters(oauth_parameters))
print(res.status_code)
# print(res.text)
print()


# https://sandbox.evernote.com/oauth?
#   &oauth_timestamp=1429572048 -- DONE in oauth_parameters
#   &oauth_signature_method=HMAC-SHA1 -- DONE in oauth_parameters
#   &oauth_version=1.0 -- DONE in oauth_parameters
#   &oauth_nonce=4078121641140961292 -- DONE in oauth_parameters
#   oauth_consumer_key=internal-dev -- DONE in oauth_parameters
#   &auth_signature=hfA8r3NdMnZbzN0OOmTZIZj6Wkc= -- DONE in oauth_parameters
#   &oauth_verifier=40793F8BAE15D4E3B6DD5CA8AB4BF62F -- DONE 
#   &auth_token=internaldev.14CD91FCE1F.687474703A2F2F6C6F63616C686F7374.6E287AD298969B6F8C0B4B1D67BCAB1D -- DONE in auth_token
