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


class CycloHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self): 
        print ('CycloHandler - get ')

        if len(cc.commits) == 0:
            commit_number = 'Done'
            
            if not cc.finished:
                cc.finished = True
                cc.FinishUp()
        else:
            commit = cc.commits.pop(0)
            commit_number = commit.hexsha
        
        self.returnData(commit_number)


    def post(self):
        #logging.info('Cyclo Server- POST')
        msg = json_decode(self.request.body)
        #print (msg['commit'])
        #print (msg['complexity'])

        commit = msg['commit']
        complexity = msg['complexity']
        duration = msg['duration']

        cc.resultsDb.append((commit, complexity, duration))
        self.finish("file result received")


application = tornado.web.Application([
    (r"/", CycloHandler),
    (r"/results", ResultsHandler)
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
        #self.CycloServerAdress = CycloServerAdress

        self.resultsDb = []
        
        #to avoid calling the finish class more thant once
        self.finished = False
    
    def FinishUp(self):
        
        df = pd.DataFrame(self.resultsDb, columns = ['Commit', 'Complexity', 'Time'])
        df['nClients'] = self.nClients
        df.to_csv('{}_{}Clients.csv'.format(self.repoName, self.nClients))

        

if __name__ == "__main__":
    application.listen(8888)

    repoUrl = "https://github.com/dmenin/statsbasic"
    
    working_dir = 'c:\\CycloComplx'
    working_folder = 'CycloServer'
    fullpath = os.path.join(working_dir, working_folder)


    nClients = 1
    cc = CycloComplx(repoUrl, fullpath, nClients)

    IOLoop.instance().start()