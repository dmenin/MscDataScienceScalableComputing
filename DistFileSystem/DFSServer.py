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
import time


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

# @gen.coroutine
# def fetch_coroutine(url):
#     http_client = AsyncHTTPClient()
#     response = yield http_client.fetch(url)
#     raise gen.Return(response.body)


from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
import json

class FileHandler(BaseHandler):
    #
    # @gen.coroutine
    # def get(url):
    #     response = yield os.listdir(fServer.fileServerRoot)
    #     raise gen.Return(response)

    # @gen.coroutine
    # def get(self):
    #     time.sleep(10)
    #     http_client = AsyncHTTPClient()
    #     response = yield http_client.fetch('http://www.gogole.com')
    #     raise gen.Return(response.body)
    #

    # def get(self):
    #     logging.info('FileHandler - GET')
    #     time.sleep(5)
    #     self.returnData(os.listdir(fServer.fileServerRoot))
    def post(self, filename):
        logging.info('FileHandler - POST')
        # result = yield self.async()
        # foo = json_decode(self.request.body)
        filecontent = self.request.body

        fullFilePath = os.path.join(FileServerRoot, filename)
        output_file = open(fullFilePath, 'w')
        output_file.write(str(filecontent))
        self.finish("file" + fullFilePath + " is uploaded")

    @gen.coroutine
    def get(self):
        url = "https://www.google.com"
        time.sleep(10)
        request = HTTPRequest(
            url=url,
            method="GET"
        )
        response = yield gen.Task(
            AsyncHTTPClient().fetch, request)

        self.returnData(os.listdir(fServer.fileServerRoot))
        #raise gen.Return(response.body)

class LockHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        url = "https://www.google.com"

        request = HTTPRequest(
            url=url,
            method="GET"
        )
        response = yield gen.Task(
            AsyncHTTPClient().fetch, request)

        self.returnData(os.listdir(fServer.fileServerRoot))

    # def get(self):
    #     logging.info('LockHandler - GET')
    #     self.returnData(lServer.listLocks())

    # @gen.coroutine
    # def get(self):
    #     http_client = AsyncHTTPClient()
    #     response = yield http_client.fetch('http://www.gogole.com')
    #     raise gen.Return(response.body)


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
    else:
        lServer = 'TODO : need to create object and read the existing locking file'

    return tornado.web.Application([
         (r"/Files", FileHandler)
        ,(r"/Files/(.*)/create", FileHandler)

        ,(r"/Locks", LockHandler)
        # ,
        # (r"/", MainHandler),
        # (r"/post", POSTHandler),
        # (r"/(.*)", PUTHandler),
        # (r"/", Something)
    ]), fServer, lServer



if __name__ == "__main__":
    # Tornado configures logging.
    options.parse_command_line()

    # Read from config File:
    port = 9998

    # Set these variables accordingly what role you want to server to perform:
    FileServerRoot    = None
    LockingServerRoot = None

    FileServerRoot    = 'c:\\DistFileSystem\\FilesRoot'
    LockingServerRoot = 'c:\\DistFileSystem\\LockRoot'

    app, fServer, lServer = make_app(FileServerRoot, LockingServerRoot, True)

    app.listen(port)
    main_loop = tornado.ioloop.IOLoop.current()

    try:
        main_loop.start()
    finally:
        main_loop.stop()