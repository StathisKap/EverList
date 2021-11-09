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
from secrets import dev_token # This is my developer token in a differnt file named secrets

# Real applications authenticate with Evernote using OAuth, but for the
# purpose of exploring the API, you can get a developer token that allows
# you to access your own Evernote account. To get a developer token, visit
# https://sandbox.evernote.com/api/DeveloperToken.action
auth_token = dev_token

if auth_token == "your developer token":
    print("Please fill in your developer token")
    print("To get a developer token, visit " \
          "https://sandbox.evernote.com/api/DeveloperToken.action")
    exit(1)

sandbox=True
china=False

client = EvernoteClient(token=auth_token, sandbox=sandbox,china=china)

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

elif  found_Shopping_List == True: # To be continued. Will pass the recipe ingredients from the C program to this and it will pass it along
    print("'Shopping List' is already there")
    current_content = note_store.getNoteContent(auth_token,Shopping_List_note_metadata.guid)
    print(current_content)
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
        print("\n******Updated******\n")