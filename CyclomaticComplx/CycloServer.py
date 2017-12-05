import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode
import os
from git import Repo
import json
import CicloGit
import pandas as pd
import datetime
import configparser


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


class ResultsHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        print('ResultsHandler - get ')
        self.returnData(cc.resultsDb)

class ReadyHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        print('ReadyHandler - ready')
        cc.serverReady = True
        cc.StartWorkTime = datetime.datetime.now()
        self.returnData('Ok Boss!')


class CycloHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self): 
        print ('CycloHandler - get ')
        if cc.serverReady == False:
            commit_number = 'Server not Ready'
        elif len(cc.commits) == 0:
            commit_number = 'Done'
            if not cc.finished:
                cc.finished = True
                cc.FinishUp()
        else:
            commit = cc.commits.pop(0)
            commit_number = commit.hexsha
        
        self.returnData(commit_number)


    def post(self):
        print ('CycloHandler - post')
        msg = json_decode(self.request.body)

        commit = msg['commit']
        complexity = msg['complexity']
        duration = msg['duration']
        clientName = msg['clientName']

        cc.resultsDb.append((commit, complexity, duration, clientName))
        self.finish("file result received")


application = tornado.web.Application([
    (r"/", CycloHandler),
    (r"/results", ResultsHandler),
    (r"/ready", ReadyHandler)
    ])


class CycloComplx(object):
    
    def __init__(self, repoUrl, fullpath, nClients):
        self.repoUrl = repoUrl
        self.repoName = os.path.basename(os.path.normpath(repoUrl))
        repo = CicloGit.cloneRepo(repoUrl, fullpath)
        commits = list(repo.iter_commits('master'))
        
        self.nClients = nClients
        #just to make debuggin easier
        self.repo = repo
        self.commits = commits
        
        #flag to prevent clients from start working one at a time
        self.serverReady = False
        
        #storesthe results
        self.resultsDb = []
        
        #to avoid calling the finish class more thant once
        self.finished = False

        self.StartWorkTime = None


    def FinishUp(self):
        totalTime = (datetime.datetime.now() - cc.StartWorkTime).seconds
        self.resultsDb.append(('Total',0,totalTime,'Server'))

        df = pd.DataFrame(self.resultsDb, columns = ['Commit', 'Complexity', 'Time', 'ClientName'])
        df['nClients'] = self.nClients
        df.to_csv('Run{}_{}_{}Clients.csv'.format(self.runUnId, self.repoName, self.nClients))



if __name__ == "__main__":
    runUnId = datetime.datetime.now().microsecond
    configParser = configparser.RawConfigParser()   
    conf = configParser.read('CycloConfig.txt')

    repoUrl = configParser.get('CycloConfig', 'repoUrl')
    working_dir = configParser.get('CycloConfig', 'working_dir')
    #repoUrl = "https://github.com/dmenin/statsbasic"    
    working_folder = 'CycloServer'

    
    fullpath = os.path.join(working_dir, working_folder)

    nClients = 2
    cc = CycloComplx(repoUrl, fullpath, nClients)
    cc.runUnId = runUnId 
    
    application.listen(8888)
    IOLoop.instance().start()