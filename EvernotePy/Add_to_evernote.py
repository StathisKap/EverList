#! /opt/homebrew/bin/python3
# Finds or creates a "Shopping List" note and adds the recipe Ingredients from Recipies.c
# Created by Stathis Kapnidis
# Feel free to modify or distribute however you want

import hashlib
import binascii
import os
import sys
import evernote.edam.type.ttypes as Types
import evernote.edam.userstore.constants as UserStoreConstants
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from secrets import dev_secret, Full_Access_Consumer_Secret, Full_Access_Consumer_Key # This is my developer token in a differnt file named secrets
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
import webbrowser
import json

##
# Helper function to turn query string parameters into a
# Python dictionary
##
def parse_query_string(authorize_url):
    uargs = authorize_url.split('?')
    vals = {}
    if len(uargs) == 1:
        raise Exception('Invalid Authorization URL')
    for pair in uargs[1].split('&'):
        key, value = pair.split('=', 1)
        vals[key] = value
    return vals

sandbox=True
china=False


############### O AUTH ####################
Oauth_Dict_json = {}

Key = Full_Access_Consumer_Key
Secret = Full_Access_Consumer_Secret

if os.path.isfile('creds.json'):
    print("Found token")
    with open('creds.json') as json_file:
        Oauth_Dict_json = json.load(json_file)
        auth_token = Oauth_Dict_json['oauth_token']
    client = EvernoteClient(token= auth_token, sandbox=sandbox,china=china)
else:
    ##
    # Create an instance of EvernoteClient using your API
    # key (consumer key and consumer secret)
    ##
    print("Please authorise app")
    client = EvernoteClient(
                consumer_key = Key,
                consumer_secret = Secret,
                sandbox = sandbox,
                china = china
            )
    ##
    # Provide the URL where the Evernote Cloud API should
    # redirect the user after the request token has been
    # generated. In this example, localhost is used
    ##
    request_token = client.get_request_token('http:127.0.0.1:8000')

    ##
    # Prompt the user to open the request URL in their browser
    ##
    webbrowser.open(client.get_authorize_url(request_token))

    ##
    # Create a Server to handle one request and receive the resulting URL
    # so we can pull it apart
    ##
    class MyRequestHandler(BaseHTTPRequestHandler):
        request = ""
        def do_GET(self):
            # print(self.path)
            MyRequestHandler.request = self.path
            message = " <div><center><span style=\"font-size: 32px;\">Success!</span></center></div>"
            self.protocol_version = "HTTP/1.1"
            self.send_response(200)
            self.send_header("Content-Length", message)
            self.end_headers()
            self.wfile.write(bytes(message, "utf8"))
        def do_POST(self):
            self.send_response(200)
            content_length = int(self.headers.get('Content-Length'))
            print(self.rfile.read(content_length))

    httpd = HTTPServer(('127.0.0.1', 8000), MyRequestHandler)
    httpd.handle_request()
    if not MyRequestHandler.request:
        print("fail"),exit(1)
    authurl  = MyRequestHandler.request

    ##
    # Parse the URL to get the OAuth verifier
    ##
    vals = parse_query_string(authurl)

    ##
    # Use the OAuth verifier and the values from request_token
    # to built the request for our authentication token, then
    # ask for it.
    ##
    auth_token = client.get_access_token(
                request_token['oauth_token'],
                request_token['oauth_token_secret'],
                vals['oauth_verifier']
            )

    ##
    # Create a new EvernoteClient instance with our auth
    # token.
    ##
    client = EvernoteClient(token=auth_token, sandbox=sandbox,china=china)

    ##
    # Test the auth token...
    ##
    userStore = client.get_user_store()
    user = userStore.getUser()

    ##
    # If our username prints, it worked.
    ##
    print("Finished OAuth")
    print(user.username)

    Oauth_Dict_json['oauth_token'] = auth_token
    with open('creds.json','w') as outfile:
        json.dump(Oauth_Dict_json, outfile)
############### OAUTH END #######################

#Checks for a URL
if len(sys.argv) < 2:
    print("No Recipe Title and Ingredients")
    exit(1)

user_store = client.get_user_store()

version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
user = user_store.getUser()
print("Is my Evernote API version up to date? ", str(version_ok))
if not version_ok:
    exit(1)

note_store = client.get_note_store()

notebooks = note_store.listNotebooks()


filter = NoteFilter()
offset = 0
max_notes = 10
result_spec = NotesMetadataResultSpec()
result_spec.includeTitle = True
print("Starting Search")
result_list = note_store.findNotesMetadata(auth_token , filter, offset, max_notes, result_spec) # Searches for all notes in the account
print("Finished Search\n")

found_Shopping_List = False
for note in result_list.notes: # Looks through all of the notes and finds the one name Shopping List. If it exists it turns a boolean to True.
    if note.title == "Shopping List":
        found_Shopping_List = True
        Shopping_List_note_metadata = note

if  found_Shopping_List != True: # If it didn't find it, then it creates it
    note = Types.Note()
    note.title = "Shopping List"

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                    '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>Recipies<br/>'
    note.content += '</en-note>'

    # Finally, send the new note to Evernote using the createNote method
    created_note = note_store.createNote(note)

    print("Successfully created the 'Shopping List' note with GUID: ", created_note.guid)
    Shopping_List_note_metadata = created_note

elif  found_Shopping_List == True: # To be continued. Will pass the recipe ingredients from the C program to this and it will pass it along
    print("'Shopping List' is already there")
current_content = note_store.getNoteContent(auth_token,Shopping_List_note_metadata.guid)
# print(current_content)
end_of_content = current_content.find('</en-note>')
if end_of_content != -1:
    if len(sys.argv) == 3:
        current_content = current_content[:end_of_content] + '<br></br>' + str(sys.argv[1]) + str(sys.argv[2]) + current_content[end_of_content:]
else:
    current_content = current_content[:end_of_content] + '<br></br>' + '<div>Test Sentence</div>' + current_content[end_of_content:]
Updated_Note = Types.Note()
Updated_Note.title = Shopping_List_note_metadata.title
Updated_Note.guid = Shopping_List_note_metadata.guid
Updated_Note.content = current_content
note_store.updateNote(auth_token,Updated_Note)
print("Added " + "'" + sys.argv[1][sys.argv[1].find("<u>")+3:sys.argv[1].find("</u>")] + "'")
print("******Updated******\n")
