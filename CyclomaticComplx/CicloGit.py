import os
from git import Repo
import shutil

def cloneRepo(repoUrl, fullpath):
    #repoUrl = "https://github.com/dmenin/statsbasic"
    
    #1)delete if client working folder exists and create
    if os.path.exists(fullpath):
        shutil.rmtree(fullpath)
    os.makedirs(fullpath)
    
    #2)dowload repo:     
    print('Cloning repo {} into directory: {}'.format(repoUrl, fullpath))
    Repo.clone_from(repoUrl, fullpath)
    print('cloning finished')
    
    repo = Repo(fullpath)
    assert not repo.bare
    
    return repo
