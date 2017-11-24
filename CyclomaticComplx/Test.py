import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import gen
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
api_key = "AIzaSyAL7uWYBJTnV3o3yGf9dBe9qF8I4aanemM"
states = {
            "NSW": "New South Whales",
            "QLD": "Queensland",
            "ACT": "Australian Capital Territory",
            "VIC": "Victoria",
            "TAS": "Tasmania",
            "SA": "South Australia"
        }
api_url = "https://www.googleapis.com/mapsengine/v1/tables/12421761926155747447-06672618218968397709/features?version=published&key={0}&where=State='{1}'"

import time
class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        url = "https://www.google.com"
        response = yield gen.Task(
            AsyncHTTPClient().fetch,url)
        print('-----')
        print (response)
        clean_response = response #scrub_it(response)

        #self.render("templates/main.html",all_locations=clean_response)
        self.write(str(clean_response).encode('utf-8'))
        self.finish()


class StatesHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        async_client = AsyncHTTPClient()

        output = []
        for k,v in states.items():
            task = gen.Task(self.get_state_data, k, async_client)
            output.append(task)

        logger.info(output)

        results = yield output
        print('-----------')
        results = dict(results)

        print (results)
        #self.render("templates/states.html", **results)

    @gen.coroutine
    def get_state_data(self, state, client):
        url = url = "https://www.google.com"
        logger.info("Getting {0}".format(state))
        output = yield gen.Task(client.fetch, url)
        logger.info("Got {0}".format(state))
        time.sleep(3)
        return (state.lower(), "Got {0}".format(state))


class StateHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, abbv):
        st = abbv.upper()
        url = "https://www.googleapis.com/mapsengine/v1/tables/12421761926155747447-06672618218968397709/features?version=published&key={0}&where=State='{1}'".format(api_key, st)
        request = HTTPRequest(
            url=url,
            method="GET"
        )
        response = yield gen.Task(
            AsyncHTTPClient().fetch,request)

        clean_response = scrub_it(response)

        self.render("templates/single_state.html",
                    locations=clean_response,
                    name=states[st])


def scrub_it(response):
    clean = json.loads(response.body.decode("utf-8"))
    if "features" in clean:
        return clean["features"]
    else:
        return [clean["error"]]


routes = [
    (r"/", MainHandler),
    (r"/states", StatesHandler),
    (r"/states/(.*)", StateHandler)
]

application = tornado.web.Application(routes, debug=True)
if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()