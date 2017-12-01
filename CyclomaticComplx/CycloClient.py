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
import numpy as np
import datetime
import configparser

class CycloClient(object):
    
    def __init__(self, repoUrl, fullpath, CycloServerAdress, MyName):
        repo = CicloGit.cloneRepo(repoUrl, fullpath)
        commits = list(repo.iter_commits('master'))
        

        self.repo = repo
        self.commits = commits
        self.CycloServerAdress = CycloServerAdress
        self.repoUrl = repoUrl
        self.fullpath = fullpath
        self.MyName = MyName

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
        repo = self.repo
     
        while True:
            startTime = datetime.datetime.now()
            
            #ask the server for a task
            response = requests.get(CycloServerAdress)
            jobID = response.json()
            
            if jobID == 'Server not Ready':
                print (jobID)
                time.sleep(1)#wait one sec
                continue
            elif jobID == 'Done': 
                break
            
            
            #change the files on disk to the specific commit
            git = repo.git
            git.checkout(jobID)
        
            #get a lit of py files to calculate complexity
            files = self.getFileList()
            
            #CALCULATE THE COMPLEXITY
            #print ('Client {} - calculating task {}'.format(MyName, task))
            c = self.calculateComplexity(files)
        
            totalTime = (datetime.datetime.now() - startTime).seconds
            
            result = {'commit': jobID, 
                      'complexity': str(c), 
                      'duration': str(totalTime),
                      'clientName': self.MyName
                     }
            print('{} completed by client {}. Complexity:{}'.format(response.text, MyName, c))
            
            #post result to the server
            response = requests.post('http://localhost:8888', json=result)

if __name__ == "__main__":
    
    configParser = configparser.RawConfigParser()   
    conf = configParser.read('CycloConfig.txt')

    repoUrl = configParser.get('CycloConfig', 'repoUrl')
    CycloServerAdress = configParser.get('CycloConfig', 'CycloServerAdress')
    working_dir = configParser.get('CycloConfig', 'working_dir')

    #repoUrl = "https://github.com/dmenin/statsbasic"
    #CycloServerAdress = "http://localhost:8888"
    #working_dir = 'c:\\CycloComplx'

    clientUnIdentifier = datetime.datetime.now().microsecond
    MyName = 'Client_{}'.format(clientUnIdentifier)
    print ('I am {}'.format(MyName))

    fullpath = os.path.join(working_dir, MyName)
    
    client = CycloClient(repoUrl, fullpath, CycloServerAdress, MyName)
    client.startWorking()
    


