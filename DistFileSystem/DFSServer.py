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

# from tornado import gen
# from tornado.httpclient import AsyncHTTPClient
# from tornado.httpclient import HTTPRequest
# import json


class FileHandler(BaseHandler):

    def get(self):
        logging.info('FileHandler - GET')
        self.returnData(os.listdir(fServer.fileServerRoot))

    def post(self, filename):
        logging.info('FileHandler - POST')
        filecontent = self.request.body

        result = fServer.createFile(filename, filecontent)

        self.finish(result)


class LockHandler(BaseHandler):

    def get(self):
        logging.info('LockHandler - GET')
        self.returnData(lServer.listLocks())

class DirectoryHandler(BaseHandler):

    def get(self):
        logging.info('DirectoryHandler - GET')
        self.returnData(dServer.listDirectories())

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

    def RequestLock(self, file, who):
        self.control[file] = Lock(file, who, datetime.datetime.now())

    def listLocks(self):
        for key in self.control:
            obj = self.control[key] # This is a Lock Object
            print(obj.file, obj.who, obj.time)


class FileServer(BaseServer):

    fileServerRoot = None

    def __init__(self, fileServerRoot, force):
        BaseServer.__init__(self, fileServerRoot, force)
        self.fileServerRoot = fileServerRoot

    def generateInternalFileName(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


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
    else:
        lServer = 'TODO : need to create object and read the existing locking file'

    if isDirectoryServer is not False:
        print ('Server is a Directory server')
        dServer = DirectoryServer()


    return tornado.web.Application([
         (r"/Files", FileHandler)
        ,(r"/Files/(.*)/create", FileHandler)

        ,(r"/Directory", DirectoryHandler)

        ,(r"/Locks", LockHandler)

        # (r"/", MainHandler),
        # (r"/post", POSTHandler),
        # (r"/(.*)", PUTHandler),
        # (r"/", Something)
    ]), fServer, lServer, dServer



if __name__ == "__main__":
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