import os
import logging
from urllib.parse import unquote
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado import options
from tornado.escape import json_encode, json_decode
import shelve
import datetime
import shutil


#GLOBAL VARIABLES
#Root file system folder folder. Will be created if doesnt exist. Inform ful path
FileServerRoot = ''
#Locking folder. Will contain on file "shelve" file that contains one file controling the locks
LockingServerRoot = ''


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


#@tornado.web.stream_request_body
class FileHandler(BaseHandler):

    def get(self):
        logging.info('FileHandler - GET')
        self.returnData(os.listdir(FileServerRoot))

    def post(self, filename):
        logging.info('FileHandler - POST')
        #result = yield self.async()
        #foo = json_decode(self.request.body)
        filecontent = self.request.body

        fullFilePath = os.path.join(FileServerRoot, filename)
        output_file = open(fullFilePath, 'w')
        output_file.write(str(filecontent))
        self.finish("file" + fullFilePath + " is uploaded")

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

    def __init__(self, LockingServerRoot, Force):
        BaseServer.__init__(self,LockingServerRoot, Force)

        self.control = shelve.open(os.path.join(LockingServerRoot, 'locks'))

    def RequestLock(self, file, who):
        self.control[file] = Lock(file, who, datetime.datetime.now())


class FileServer(BaseServer):

    def __init__(self, fileServerRoot, force):
        BaseServer.__init__(self, fileServerRoot, force)

'''
Creates all pre-requisites + return WebApplication with Handlers
ForceResert = recreate folder
'''
def make_app(FileServerRoot, LockingServerRoot, ForceResert):

    if FileServerRoot is not None:
        print ('Server is a file server')
        fServer = FileServer(FileServerRoot, ForceResert)

    if LockingServerRoot is not None:
        print ('Server is a locking server')
        lServer = LockingServer(LockingServerRoot, ForceResert)
        lServer.RequestLock('a','b')

    return tornado.web.Application([
         (r"/Files", FileHandler)
        ,(r"/Files/(.*)/create", FileHandler)

        # ,
        # (r"/", MainHandler),
        # (r"/post", POSTHandler),
        # (r"/(.*)", PUTHandler),
        # (r"/", Something)
    ])


    def __init__(self, LockingRoot):
        pass

if __name__ == "__main__":
    # Tornado configures logging.
    options.parse_command_line()

    #Read from config File:
    port = 9998

    #Set these variables accordingly what role you want to server to perform:
    FileServerRoot    = None
    LockingServerRoot = None

    FileServerRoot    = 'c:/DistFileSystem/FilesRoot'
    LockingServerRoot = 'c:/DistFileSystem/LockRoot'

    app = make_app(FileServerRoot, LockingServerRoot, True)

    app.listen(port)
    main_loop = tornado.ioloop.IOLoop.current()

    try:
        main_loop.start()
    finally:
        main_loop.stop()