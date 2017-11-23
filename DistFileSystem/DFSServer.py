import os
import logging
from urllib.parse import unquote
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado import options
from tornado.escape import json_encode, json_decode
import shelve

#GLOBAL VARIABLES
#Root file system folder folder. Will be created if doesnt exist. Inform ful path
FileServerRoot = ''
#Locking folder. Will contain on file "shelve" file that contains one file controling the locks
LockingServerRoot = ''
LockControl = None

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
Creates all pre-requisites + retur WebApplication with Handlers
'''
def make_app(FileServerRoot, LockingServerRoot):

    if FileServerRoot != None:
        print ('Server is a file server')
        if not os.path.exists(FileServerRoot):
            os.makedirs(FileServerRoot)

    if LockingServerRoot != None:
        print ('Server is a locking server')
        if not os.path.exists(LockingServerRoot):
            os.makedirs(LockingServerRoot)
            LockControl = shelve.open(os.path.join(LockingServerRoot, 'locks'))


    return tornado.web.Application([
         (r"/Files", FileHandler)
        ,(r"/Files/(.*)/create", FileHandler)

        # ,
        # (r"/", MainHandler),
        # (r"/post", POSTHandler),
        # (r"/(.*)", PUTHandler),
        # (r"/", Something)
    ])

class LockingServer():

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

    app = make_app(FileServerRoot, LockingServerRoot)

    app.listen(port)
    main_loop = tornado.ioloop.IOLoop.current()

    try:
        main_loop.start()
    finally:
        main_loop.stop()