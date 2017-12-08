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
import requests

# GLOBAL VARIABLES
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


class ReplicationHandler(BaseHandler):
    def get(self, file=None):
        logging.info('ReplicationHandler - GET')
        if file is None:
            self.returnData(os.listdir(rServer.replicationServerRoot))
        else:
            self.returnData(rServer.getFile(file))

    def post(self, filename):
        filecontent = str(self.request.body.decode('utf8'))  # removes the 'b
        if rServer.checkIfExists(filename):
            logging.info('FileHandler - POST: Update File')
            result = rServer.updateFile(filename, filecontent)
        else:
            logging.info('FileHandler - POST: Create File')
            result = rServer.createFile(filename, filecontent)

        self.finish(result)
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

class ReplicationServer(BaseServer):
    def __init__(self, replicationServerRoot, force):
        self.replicationServerRoot = replicationServerRoot
        BaseServer.__init__(self, self.replicationServerRoot, force)

    def checkIfExists(self, filename):
        p = pathlib.Path(os.path.join(self.replicationServerRoot, filename))
        return p.is_file()

    def updateFile(self, filename, filecontent):
        fullFilePath = os.path.join(self.replicationServerRoot, filename)

        with open(fullFilePath, 'w') as output_file:
            output_file.write(str(filecontent))

        return ' - File {} updated on replica server'.format(filename)

    def getFile(self, file):
        with open(os.path.join(self.replicationServerRoot, file), 'r') as f:
            return f.read()

    def createFile(self, internalFileName, filecontent):
        fullFilePath = os.path.join(self.replicationServerRoot, internalFileName)

        output_file = open(fullFilePath, 'w')
        output_file.write(str(filecontent))

        return ' - File {} created on replica server'.format(internalFileName)

'''
Creates all pre-requisites + return WebApplication with Handlers
ForceResert = recreate folder
'''


def make_app(ReplicationServerRoot, ForceResert):
    rServer = None

    if ReplicationServerRoot is not None:
        print('Server acts as Replication Server')
        rServer = ReplicationServer(ReplicationServerRoot, ForceResert)

    return tornado.web.Application([
         (r"/Replication", ReplicationHandler)
        , (r"/Replication/(.*)/", ReplicationHandler)
        , (r"/Replication/(.*)/create", ReplicationHandler)

    ]), rServer


if __name__ == "__main__":

    # Set these variables accordingly what role you want to server to perform:
    ReplicationServerRoot = None
    ReplicationServerRoot = 'c:\\DistFileSystem\\ReplicationRoot'
    port = 9999

    ###########################################################################
    #    #Uncomment this to run from the command so each server can perform one role
    #    parser = argparse.ArgumentParser()
    #    parser.add_argument('--rport', default='False', help='Replication Server port.')

    #
    #    args, unparsed = parser.parse_known_args()
    #    print (args)
    #    print (args.fport)
    #    if args.rport !=0:
    #        port = int(args.rport)
    ##########################################################################

    app, rServer = make_app(ReplicationServerRoot, True)

    app.listen(port)
    main_loop = tornado.ioloop.IOLoop.current()

    try:
        main_loop.start()
    finally:
        main_loop.stop()