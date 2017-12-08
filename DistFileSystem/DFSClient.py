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
                                     format(locking_server, file)).json()
            if clientMd5 != serverMd5:
                os.remove(os.path.join(self.local_working_folder, file))
                del self.cache[file]
                return (False,
                        'Server has a different version of the file. Request it from the server. Deleting cached version.')
            else:
                print('Client has an up-to-date version of the file. Getting it locally')
                return (True, os.path.join(self.local_working_folder, file))


class DFSClient(object):
    
    def __init__(self):
        self.clientUnIdentifier = datetime.datetime.now().microsecond
        self.local_working_folder = 'c:\\DistFileSystem\\Client{}'.format(self.clientUnIdentifier)
        os.makedirs(self.local_working_folder)
        
        self.localCaching = LocalCaching(self.local_working_folder)
    
    def createFile(self, filename='foo',  content='bar'):
        # Create a file
        response = requests.post('{}/Files/{}/create'.format(file_server, filename), 
                                 data=content)
        r = response.json()
    
        # Adds the file server to the response
        r['server'] = file_server
    
        # post the new file to the directory server
        response = requests.post('{}/Directory'.format(directory_server), json=r)

    def openFile(self, fileName):
        print('Opening {}'.format(fileName))
        #1) asks the directory server where the file is and what it is called:
        response = requests.get('{}/Directory/{}/'.format(directory_server, fileName)).json()
        responseFileServer = response[0]
        responseFileInternalName = response[1]
    
        #2) checks Local Cache
        hasFile, msg = self.localCaching.checkLocalCache(responseFileInternalName)
        if not hasFile: # if it is not on the local cache
            print(msg)
            # asks the locking server if file is available:
            print(requests.get('{}/Locks/{}/'.format(locking_server, fileName)).json())
            
            # request a Lock:
            data = {'action': 'RequestLock', 'who': 'Client1'}
            print(requests.post('{}/Locks/{}/'.format(locking_server, fileName), json=data).text)
        
            # asks the file server for the file and creates a local copy
            localFilePath = os.path.join(self.local_working_folder, responseFileInternalName)
            with open(localFilePath, "w") as local_copy:
                local_copy.write(requests.get('{}/Files/{}/'.format(responseFileServer, responseFileInternalName)).json())
        
        return responseFileInternalName
    
    
    def writeToFile(self, responseFileInternalName, newLine):
        localFilePath = os.path.join(self.local_working_folder, responseFileInternalName)
        with open(localFilePath, "a") as local_copy:
            local_copy.write('\n{}'.format(newLine))
    
    #posts it back to the file server - no need to interact with Directory server at this stage anymore
    def closeAndPostBackToServer(self, fileName, responseFileInternalName):
        #posts local copy back to the server
        localFilePath = os.path.join(self.local_working_folder, responseFileInternalName)
        with open(localFilePath, "r") as local_copy:
            changed_file = local_copy.read()
        response = requests.post('{}/Files/{}/create'.format(file_server, responseFileInternalName), data=changed_file)
        print(response.text)
        
        # adds to the local cache
        self.localCaching.cache[responseFileInternalName] = self.localCaching.md5(localFilePath)
                
        # release the lock:
        data = {'action': 'ReleaseLock'}
        result = requests.post('{}/Locks/{}/'.format(locking_server, fileName), json=data)
        if result.status_code == 200:
            print(result.text)
        
    def showFiles(self):
        return requests.get("{}/Files".format(file_server)).json()
    
    def showDirectories(self):
        return requests.get("{}/Directory".format(directory_server)).json()
    
    def showLocks(self):
        return requests.get("{}/Locks".format(locking_server)).json()

    def showReplicatedFiles(self):
        return requests.get("{}/Replication".format('http://localhost:9999')).json()

#Instantiate a client
c1 = DFSClient()

#Create File
c1.createFile('MyFile1', 'This is my first file')
c1.showFiles()
c1.showDirectories()
c1.showReplicatedFiles()

#Open a file
localtoken = c1.openFile('MyFile1')

#Show the locks
c1.showLocks()

#Write to the file
c1.writeToFile(localtoken, 'This is line 2')
c1.writeToFile(localtoken, 'This is line 3')
c1.writeToFile(localtoken, 'This is line 4')

#Close the File
c1.closeAndPostBackToServer('MyFile1', localtoken)

c1.localCaching.cache



#Opening same file again - caching kicks in
localtoken = c1.openFile('MyFile1')
c1.writeToFile(localtoken, 'This is line 5')
c1.closeAndPostBackToServer('MyFile1', localtoken)


c2 = DFSClient()
localtoken = c2.openFile('MyFile1')
c2.writeToFile(localtoken, 'This is client 2 writing line 6')
c2.closeAndPostBackToServer('MyFile1', localtoken)




localtoken = c1.openFile('MyFile1')
c1.writeToFile(localtoken, 'This is client 1 again \n  writing line 7 (Well, I think its \n6 but its actually 7)')
c1.closeAndPostBackToServer('MyFile1', localtoken)
