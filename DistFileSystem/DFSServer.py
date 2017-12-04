import os
import logging
import random
from urllib.parse import unquote
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado import options
from tornado.escape import json_encode, json_decode
import shelve
import datetime
import shutil
import time
import string
import random
import pathlib
import hashlib
import argparse


#GLOBAL VARIABLES
fServer = None
lServer = None

'''
BaseHandler Class; Inherits from tornado.web.RequestHandler
Used for common methods across all other Handlers
'''
class BaseHandler(tornado.web.RequestHandler):

    def send_json_cors_headers(self):
        self.set_header("Content-Type", "application/json;")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT')

    def returnData(self, data):
        self.send_json_cors_headers()
        self.write(json_encode(data))
        self.finish()

class FileInfoHandler(BaseHandler):

    def get(self,  file):
        logging.info('FileInfoHandler - GET')
        md5 = fServer.getFileMd5(file)
        print ('File {} - MD5: {}'.format(file, md5))
        self.returnData(md5)

class FileHandler(BaseHandler):

    def get(self,  file=None):
        logging.info('FileHandler - GET')
        if file is None:
            self.returnData(os.listdir(fServer.fileServerRoot))
        else:
            self.returnData(fServer.getFile(file))

    def post(self, filename):
        filecontent = str(self.request.body.decode('utf8')) #removes the 'b
        if fServer.checkIfExists(filename):
            logging.info('FileHandler - POST: Update File')
            result = fServer.updateFile(filename, filecontent)
        else:
            logging.info('FileHandler - POST: Create File')
            result = fServer.createFile(filename, filecontent)

        self.finish(result)


class LockHandler(BaseHandler):

    def get(self, file=None):
        logging.info('LockHandler - GET')
        if file is None:
            self.returnData(lServer.listLocks())
        else:
            self.returnData(lServer.getLock(file))

    def post(self, filename):
        msg = json_decode(self.request.body)
        action = msg['action']

        if action == 'RequestLock':
            logging.info('LockHandler - POST: Request Lock')
            who = msg['who']
            result = lServer.RequestLock(filename, who)
        elif action == 'ReleaseLock':
            logging.info('LockHandler - POST: Release Lock')
            result = lServer.ReleaseLock(filename)
        else:
            pass #Error

        self.finish(result)



class DirectoryHandler(BaseHandler):

    def get(self, file=None):
        logging.info('DirectoryHandler - GET')
        if file is None:
            self.returnData(dServer.listDirectories())
        else:
            self.returnData(dServer.getMapping(file))

    def post(self):
        logging.info('DirectoryHandler - POST')
        dircontent = json_decode(self.request.body)
        print (dircontent )
        dServer.addMapping(dircontent['filename'], dircontent['server'], dircontent['internalFileName'])

        self.finish('Mapping added')


'''
Lock Class
'''
class Lock(object):

    def __init__(self, file, who, time):
        self.file = file
        self.who = who

        self.time = time


'''
Base Class for the servers.
Contains common methods like create base folder for example
'''


class BaseServer(object):

    def __init__(self, ServerRoot, Force):
        if os.path.exists(ServerRoot):  # if the folder exists
            if Force:  # if we want to force a new start
                shutil.rmtree(ServerRoot)  # delete folder
                os.makedirs(ServerRoot)  # create folder
        else:
            os.makedirs(ServerRoot)


class LockingServer(BaseServer):

    LockingServerRoot = None

    def __init__(self, LockingServerRoot, Force):
        BaseServer.__init__(self, LockingServerRoot, Force)
        self. LockingServerRoot = LockingServerRoot

        self.control = shelve.open(os.path.join(LockingServerRoot, 'locks'))

    def getLock(self, file):
        if file in self.control:
            l = self.control[file]
            return 'Lock on file {} granted to {} at {}'.format(l.file, l.who, l.time)
        else:
            return 'OK'

    def RequestLock(self, file, who):
        n = datetime.datetime.now()
        self.control[file] = Lock(file, who, n)
        return 'Lock on file {} granted to {} at {}'.format(file, who, n)

    def ReleaseLock(self, file):
        del self.control[file]
        return 'Released Lock on file {}'.format(file)

    def listLocks(self):
        l = []
        for key in self.control:
            obj = self.control[key] # This is a Lock Object
            l.append((str(obj.file), str(obj.who), str(obj.time)))

        return l

class FileServer(BaseServer):

    fileServerRoot = None

    def __init__(self, fileServerRoot, force):
        BaseServer.__init__(self, fileServerRoot, force)
        self.fileServerRoot = fileServerRoot

    def getFileMd5(self, fname):
        fullFilePath = os.path.join(self.fileServerRoot, fname)
        hash_md5 = hashlib.md5()
        with open(fullFilePath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def generateInternalFileName(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

    def checkIfExists(self, filename):
        p = pathlib.Path(os.path.join(self.fileServerRoot, filename))
        return p.is_file()

    def updateFile(self, filename, filecontent):
        fullFilePath = os.path.join(self.fileServerRoot, filename)

        with open(fullFilePath, 'w') as output_file:
            output_file.write(str(filecontent))

        return 'File {} updated'.format(filename)


    def createFile(self, filename, filecontent):
        internalFileName = self.generateInternalFileName()

        fullFilePath = os.path.join(FileServerRoot, internalFileName)
        output_file = open(fullFilePath, 'w')
        output_file.write(str(filecontent))
        result = {
            'filename' : filename,
            'internalFileName': internalFileName
        }
        return result

    def getFile(self, file):
        with open(os.path.join(self.fileServerRoot, file), 'r') as f:
            return f.read()

class DirectoryServer():

    def __init__(self):
        #contains the mapping between user readable file name and Server\file name on the server
        self.mapper = {}

    def addMapping(self, filename, server, internalFileName):
        self.mapper[filename] = (server, internalFileName)

    def getMapping(self, file):
        #Todo: deal with missing values? - shouldnt ever happen, but just in case
        return self.mapper[file]

    def listDirectories(self):
        #prints on the console
        for key in self.mapper:
            obj = self.mapper[key] #This is a tuple of server\name
            print(key, obj[0], obj[1])
        return self.mapper

'''
Creates all pre-requisites + return WebApplication with Handlers
ForceResert = recreate folder
'''
def make_app(FileServerRoot, LockingServerRoot, isDirectoryServer, ForceResert):

    if FileServerRoot is not None:
        print ('Server is a file server')
        fServer = FileServer(FileServerRoot, ForceResert)

    if LockingServerRoot is not None:
        print ('Server is a locking server')
        lServer = LockingServer(LockingServerRoot, ForceResert)

    if isDirectoryServer is not False:
        print ('Server is a Directory server')
        dServer = DirectoryServer()


    return tornado.web.Application([
         (r"/Files", FileHandler)
        ,(r"/Files/(.*)/", FileHandler)
        ,(r"/Files/(.*)/create", FileHandler)
        ,(r"/File/(.*)/getFileMd5", FileInfoHandler)

        ,(r"/Directory", DirectoryHandler)
        ,(r"/Directory/(.*)/", DirectoryHandler)

        ,(r"/Locks", LockHandler)
        ,(r"/Locks/(.*)/", LockHandler)
        ,(r"/Locks/(.*)/lock", LockHandler)

    ]), fServer, lServer, dServer



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args, unparsed = parser.parse_known_args()

    # Tornado configures logging.
    options.parse_command_line()

    # Read from config File:
    port = 9998

    # Set these variables accordingly what role you want to server to perform:
    FileServerRoot    = None
    LockingServerRoot = None
    isDirectoryServer   = False

    FileServerRoot    = 'c:\\DistFileSystem\\FilesRoot'
    LockingServerRoot = 'c:\\DistFileSystem\\LockRoot'
    isDirectoryServer   = True

    app, fServer, lServer, dServer = make_app(FileServerRoot, LockingServerRoot, DirectoryServer, True)

    app.listen(port)
    main_loop = tornado.ioloop.IOLoop.current()

    try:
        main_loop.start()
    finally:
        main_loop.stop()