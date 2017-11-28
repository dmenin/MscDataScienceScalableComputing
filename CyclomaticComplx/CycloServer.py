import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.escape import json_encode, json_decode
import os
from git import Repo


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


class CycloComplx(object):
    
    def __init__(self, working_dir, working_folder='tmp'):
    
        repo_dir = os.path.join(working_dir, working_folder)
        
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
    
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
        
        if not os.listdir(repo_dir):
            print('cloning repository into directory: {0}'.format(repo_dir))
            Repo.clone_from("https://github.com/dmenin/Crypto", repo_dir)
            print('cloning finished') 
        
        
        repo = Repo(repo_dir)
        assert not repo.bare
        
        self.commits = list(repo.iter_commits('master'))
        print("Repository setup complete")
    
    
    
    
    
#    
#    heads = repo.heads
#    master = heads.master
#    tags = repo.tags
#    print("heads = {0}, \nmaster = {1} \ntags = {2}".format(heads, master, tags))
#    print("tag0.tag = {0}".format(tags[0].tag))
#    print("tag0.commit = {0}".format(tags[0].commit))
    
#    
#    fifty_first_commits = list(repo.iter_commits('master', max_count=50))
#    all_commits = list(repo.iter_commits('master'))
#    print("First fifty commits = {0}".format(fifty_first_commits))
#    print("All commits = {0}".format(all_commits))
#    print("LEN of All commits = {0}".format(len(all_commits)))
#    
#    first_commit = all_commits[-1]
#    print("first ever commit = ", first_commit.hexsha)
#    # repo.commit(first_commit.hexsha)
#    
#    print("current hexsha = ", repo.head.object.hexsha)
#    
#    git = repo.git
#    # git.checkout(all_commits[-1].hexsha)
#    git.checkout(all_commits[0].hexsha)
#    
#    
#    ################## get all files from repo ####################
#    
#    from os import walk
#    
#    files = []
#    for (dirpath, dirnames, filenames) in walk(repo_dir):
#        for filename in filenames:
#            if '.py' in filename:
#                dirpath = dirpath.replace("\\", "/")
#                print(dirpath + '/' + filename)
#                files.append(dirpath + '/' + filename)
#    
#    # print("Files = ", f)
#    
#    ################## calculate cyclomatic complexity ####################
#    
#    
#    from radon.visitors import ComplexityVisitor
#    import radon
#    
#    
#    with open(files[10]) as f:
#        data = f.read()
#        print(data)
#    
#        dat2 = '''
#    def factorial(n):
#        if n < 2: return 1
#        return n * factorial(n - 1)
#    def foo(bar):
#        return sum(i for i in range(bar ** 2) if bar % i)
#        '''
#    
#        # v = ComplexityVisitor.from_code(data)
#        # print("Complexity = ", v.)
#        cc = radon.complexity.cc_visit(data)
#        for cc_item in cc:
#            print("complexity = ", cc_item.complexity)
#            
#            
        
        
    
        
        

if __name__ == "__main__":
    application.listen(8888)
    working_dir = 'c:\\CycloComplx'
    nClients = 1
    working_folder = 'tmp'
    
    cc = CycloComplx(working_dir, working_folder)

    IOLoop.instance().start()