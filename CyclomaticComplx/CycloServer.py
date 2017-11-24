import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode


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
        if len(things_to_do) == 0:
            task = 'Done'
        else:
            task = things_to_do.pop(0)

        self.returnData(task)

    def post(self):
        #logging.info('FileHandler - POST')
        # result = yield self.async()
        # foo = json_decode(self.request.body)
        msg = self.request.body
        print (msg)
        self.finish("file result received")


application = tornado.web.Application([
    (r"/", CycloHandler),
    ])


if __name__ == "__main__":
    application.listen(8888)
    IOLoop.instance().start()