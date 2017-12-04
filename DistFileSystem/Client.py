import requests
import random
import datetime
import os
import time
import hashlib


file_server = 'http://localhost:9998' 
directory_server = 'http://localhost:9998' 
locking_server = 'http://localhost:9998' 

class LocalCaching(object):
    
    def __init__(self, local_working_folder):
        self.cache = {}
        self.local_working_folder = local_working_folder
    
    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    
    def checkLocalCache(self, file):
        if file not in self.cache:
            return (False, 'Not on Local Cache -> go to server')
        else:
            clientMd5 = self.cache[file]
            serverMd5 = requests.get('{}/File/{}/getFileMd5'.
                                                     format(locking_server, responseFileInternalName)).json()
            if clientMd5 != serverMd5:
                os.remove(os.path.join(self.local_working_folder, file))
                del self.cache[file]
                return (False, 'Server has a different version of the file. Request it from the server. Deleting cached version.')
            else:
                print ('Client has an up-to-date version of the file. Getting it locally')
                return (True , os.path.join(self.local_working_folder, file))

#file = responseFileInternalName
#cache = localCaching.cache
###SET UP
clientUnIdentifier = datetime.datetime.now().microsecond
local_working_folder = 'c:\\DistFileSystem\\Client{}'.format(clientUnIdentifier)
os.makedirs(local_working_folder)

localCaching = LocalCaching(local_working_folder)


for i in range(5):
    #Create a file
    response = requests.post('{}/Files/file{}/create'.format(file_server, i), data="This is File{}".format(i))
    r = response.json()
    
    #Adds the file server to the response
    r['server'] = file_server 
    
    
    #post the new file to the directory server
    response = requests.post('{}/Directory'.format(directory_server), json=r)
    

requests.get("{}/Files".format(file_server)).json()
requests.get("{}/Directory".format(directory_server)).json()
requests.get("{}/Locks".format(locking_server)).json()


###############################################################################
#1) Client wants to open a file, edit and post it back to the server

#Get list of files
listOfFiles = requests.get("http://localhost:9998/Directory").json()
#choose one at random
fileName = random.choice(list(listOfFiles.items()))[0]

#asks the directory server where the file is and what it is called:
response = requests.get('{}/Directory/{}/'.format(directory_server, fileName)).json()
responseFileServer = response[0]
responseFileInternalName = response[1]


#Check Local Cache
hasFile, msg = localCaching.checkLocalCache(responseFileInternalName)
if not hasFile:
    print (msg)


#asks the locking server if file is available:
print(requests.get('{}/Locks/{}/'.format(locking_server, fileName)).json())

#request a Lock:
data = {'action': 'RequestLock', 'who': 'Client1'}
print(requests.post('{}/Locks/{}/'.format(locking_server, fileName), json=data).text)



#Simulate another client asking for the lock - anything different than OK mean the lock cant be granted:
print(requests.get('{}/Locks/{}/'.format(locking_server, fileName)).json())


#asks the file server for the file, creates a local copy and change it
localFilePath = os.path.join(local_working_folder, responseFileInternalName)
with open(localFilePath , "w") as local_copy:
    local_copy.write(requests.get('{}/Files/{}/'.format(responseFileServer, responseFileInternalName)).json())
    local_copy.write('\n Client1 writing to the file at {}'.format(datetime.datetime.now()))


#posts it back to the file server - no need to interact with Directory server at this stage anymore
def readLocalFileAndPostToServer(localFilePath, file_server, responseFileInternalName):
    with open(localFilePath , "r") as local_copy:
        changed_file = local_copy.read()
    response = requests.post('{}/Files/{}/create'.format(file_server, responseFileInternalName), data=changed_file)
    print (response.text)


readLocalFileAndPostToServer(localFilePath, file_server, responseFileInternalName)

#adds to the local cache
#It needs to be after the post to the server otherwise the server will have an earlier 
#version than the client - rendering the caching obsolete
localCaching.cache[responseFileInternalName] = localCaching.md5(localFilePath)

#release the lock:
data = {'action': 'ReleaseLock'}
print(requests.post('{}/Locks/{}/'.format(locking_server, fileName), json=data).text)


###############################################################################
#2) Use Case 2 - Test Caching on Client1 - should not fetch the same file twice:
#request same file
msg = localCaching.checkLocalCache(responseFileInternalName)
localFilePath = msg[1]

with open(localFilePath , "a") as local_copy:
    local_copy.write('\n Client1 writing to the file at {} - from cached copy'.format(datetime.datetime.now()))
readLocalFileAndPostToServer(localFilePath, file_server, responseFileInternalName)

###############################################################################
#3) Use case 3 - Second Client Updates the same file
#set up client2
client2UnIdentifier = datetime.datetime.now().microsecond
local_working_folderc2 = 'c:\\DistFileSystem\\Client{}'.format(client2UnIdentifier)
os.makedirs(local_working_folderc2)


localCaching2 = LocalCaching(local_working_folderc2)
hasFile, msg = localCaching2.checkLocalCache(responseFileInternalName)
if not hasFile:
    print (msg)
    
#write to the local copy
localFilePath2 = os.path.join(local_working_folderc2, responseFileInternalName)
with open(localFilePath2, "w") as local_copy:
    local_copy.write(requests.get('{}/Files/{}/'.format(responseFileServer, responseFileInternalName)).json())
    local_copy.write('\n Client2 writing to the file at {}'.format(datetime.datetime.now()))

#update cache
localCaching2.cache[responseFileInternalName] = localCaching2.md5(localFilePath2)
readLocalFileAndPostToServer(localFilePath2, file_server, responseFileInternalName)

###############################################################################
#4) Use case 4 - client 1 goes again
msg = localCaching.checkLocalCache(responseFileInternalName)
localFilePath = msg[1]

localFilePath = os.path.join(local_working_folder, responseFileInternalName)
with open(localFilePath , "w") as local_copy:
    local_copy.write(requests.get('{}/Files/{}/'.format(responseFileServer, responseFileInternalName)).json())
    local_copy.write('\n Client1 writing to the file from new server copy at {}'.format(datetime.datetime.now()))

readLocalFileAndPostToServer(localFilePath, file_server, responseFileInternalName)