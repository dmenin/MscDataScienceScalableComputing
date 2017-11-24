import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode
import requests
from random import *


CycloServerAdress = "http://localhost:8888"

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

    def get(self):
        while True:
            response = requests.get(CycloServerAdress)
            task = response.text
            if task == 'Done':
                break

            msg = response.text + 'done!'

            response = requests.post('http://localhost:8888', data='{}'.format(msg))

            # def post(self):
    #     #logging.info('FileHandler - POST')
    #     # result = yield self.async()
    #     # foo = json_decode(self.request.body)
    #     msg = self.request.body
    #     print (msg)
    #     self.finish("file result received")


application = tornado.web.Application([
    (r"/Start", CycloHandler),
    ])


def calculateComplexity():
    howLong = randint(1, 5)
    time.sleep(howLong)
    return howLong 


if __name__ == "__main__":
    #not using REST...yet(?)
    #application.listen(8887)
    #IOLoop.instance().start()
    
    MyName = 'Client_{}'.format(randint(1, 100))
    print ('I am {}'.format(MyName))
    
    CycloServerAdress = "http://localhost:8888"
    while True:
        #ask the server for a task
        response = requests.get(CycloServerAdress)
        task = response.text
        if task == '"Done"': #deal with the double quotes
            break
        
        #CALCULATE THE COMPLEXITY
        print ('Client {} - calculating task {}'.format(MyName, task))
        c = calculateComplexity()
        
        
        msg = '{} completed by client {}. Complexity:{}'.format(response.text, MyName, c)
        
        #post result to the server
        response = requests.post('http://localhost:8888', data='{}'.format(msg))




