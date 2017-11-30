import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode
import os
from git import Repo
import json
import CicloGit


#this is the list of files to calculate the complexity
things_to_do = ['task1', 'task2', 'task3', 'task4', 'task5']

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



class CycloHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self): 
        print ('CycloHandler - get ')

        if len(cc.commits) == 0:
            commit_number = 'Done'
        else:
            commit = cc.commits.pop(0)
            commit_number = commit.hexsha
        
        self.returnData(commit_number)


    def post(self):
        #logging.info('Cyclo Server- POST')
        msg = json_decode(self.request.body)
        print (msg['commit'])
        print (msg['complexity'])
        self.finish("file result received")


application = tornado.web.Application([
    (r"/", CycloHandler),
    ])


class CycloComplx(object):
    
    def __init__(self, repoUrl, fullpath):
        repo = CicloGit.cloneRepo(repoUrl, fullpath)
        commits = list(repo.iter_commits('master'))
        
        #just to make debuggin easier
        self.repo = repo
        self.commits = commits
        #self.CycloServerAdress = CycloServerAdress
        
        

if __name__ == "__main__":
    application.listen(8888)

    repoUrl = "https://github.com/dmenin/statsbasic"
    working_dir = 'c:\\CycloComplx'
    working_folder = 'CycloServer'
    fullpath = os.path.join(working_dir, working_folder)


    nClients = 1
    cc = CycloComplx(repoUrl, fullpath)

    IOLoop.instance().start()