import os
import time
import shutil
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode
import requests
from random import *
from radon.complexity import cc_rank, cc_visit
import radon
import CicloGit
from datetime import datetime
import numpy as np

CycloServerAdress = "http://localhost:8888"
#
# class BaseHandler(tornado.web.RequestHandler):
#
#     def send_json_cors_headers(self):
#         self.set_header("Content-Type", "application/json;")
#         self.set_header("Access-Control-Allow-Origin", "*")
#         self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
#         self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT')
#
#     def returnData(self, data):
#         self.send_json_cors_headers()
#         self.write(json_encode(data))
#         self.finish()
#
#
# class CycloHandler(BaseHandler):
#
#     def get(self):
#         while True:
#             response = requests.get(CycloServerAdress)
#             task = response.text
#             if task == 'Done':
#                 break
#
#             msg = response.text + 'done!'
#
#             response = requests.post('http://localhost:8888', data='{}'.format(msg))
#
#             # def post(self):
#     #     #logging.info('FileHandler - POST')
#     #     # result = yield self.async()
#     #     # foo = json_decode(self.request.body)
#     #     msg = self.request.body
#     #     print (msg)
#     #     self.finish("file result received")
#
#
#application = tornado.web.Application([
#    (r"/Start", CycloHandler),
#    ])


class CycloClient(object):
    
    def __init__(self, repoUrl, fullpath, CycloServerAdress):
        repo = CicloGit.cloneRepo(repoUrl, fullpath)
        commits = list(repo.iter_commits('master'))
        

        self.repo = repo
        self.commits = commits
        self.CycloServerAdress = CycloServerAdress
        self.repoUrl = repoUrl
        self.fullpath = fullpath

    def getFileList(self):
        files = []
    
        for (dirpath, dirnames, filenames) in os.walk(self.fullpath):
            for filename in filenames:
                if '.py' in filename:
                    files.append(os.path.join(dirpath, filename))
        return files

    def calculateComplexity(self, files):
        def calc(f):
            total = 0
            try:
                raw = open(f).read()
                complx = radon.complexity.cc_visit(raw)
                total = np.sum([c.complexity for c in complx])
            except Exception as err:
                #for the sake of simplicity we'll just ignore failures
                pass
            
            return total 

        return np.sum([calc(f) for f in files])

    
    def startWorking(self):
        
        #TO DO :check with the server if it is ready to avoind one client starting before the others
        repo = self.repo
        #repo = client.repo
        
        while True:
            startTime = datetime.now()
            #ask the server for a task
            response = requests.get(CycloServerAdress)
            jobID = response.json()
            
            if jobID == 'Done': #do something here
                break
            
            #change the files on disk to the specific commit
            git = repo.git
            git.checkout(jobID)
        
            #get a lit of py files to calculate complexity
            files = self.getFileList()
            
            #CALCULATE THE COMPLEXITY
            #print ('Client {} - calculating task {}'.format(MyName, task))
            c = self.calculateComplexity(files)
        
            totalTime = (datetime.now() - startTime).seconds
            
            result = {'commit': jobID, 'complexity': str(c), 'duration': str(totalTime)}
            print('{} completed by client {}. Complexity:{}'.format(response.text, MyName, c))
            
            #post result to the server
            response = requests.post('http://localhost:8888', json=result)



#import sqlite3
#db = sqlite3.connect(':memory:')
#
#db.tables
#        
#self.commits = list(self.)
#        # self.cc_per_commit = {commit: None for commit in self.commits}
#        self.cc_per_commit = {}
#
#        print("Repository setup complete")    
        
if __name__ == "__main__":
    #not using REST...yet(?)
    #application.listen(8887)
    #IOLoop.instance().start()
    
    repoUrl = "https://github.com/dmenin/statsbasic"
    CycloServerAdress = "http://localhost:8888"
    working_dir = 'c:\\CycloComplx'

    
    #TODO: need to be better at this to avoid duplication
    clientUnIdentifier = randint(1, 1000)
    MyName = 'Client_{}'.format(clientUnIdentifier)
    print ('I am {}'.format(MyName))

    fullpath = os.path.join(working_dir, MyName)
    
    client = CycloClient(repoUrl, fullpath, CycloServerAdress)
    client.startWorking()