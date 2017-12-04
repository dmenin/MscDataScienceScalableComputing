# Scalable Computing

#### <i class="icon-file"></i> Ciclo Complexity:

* Assumptions:

1) Both, server and each client, will have a copy of the repo. I want to avoid adding the network transmission time and focus on the time it takes to do the calculation
2) All relevant information should be read from the GlobalConfig file
3) Server will start, dowload the repo into the "CycloServer" folder and stay on a "not ready" state until told otherwise. This is to make sure all clients get to work at the same time.
4) Start as many clients as needed. Each one will download the repo and start asking the server for work. Server will respond "not ready"
5) Make "get" server call to "/ready". This will make the server start handling out jobs.
6) Once there are no more jobs. Clients die and server outputs final final on the fomart: "{UnIdentifier}{RepoName}_{nClients}Clients.csv'




#### <i class="icon-file"></i> Chat Server:
```
// Running:
python ChatServer.py --host localhost --port 1234
```

or (Unix only):

```
start.sh --host=<host ip> --port=<port>
```


###<i class="icon-file"></i> Distributed File System:

#### Assumptions:
* Directory\File Server: store all files in a file server in a flat file system (i.e. each file server provides a single directory in effect), requiring the directory server to maintain mapping of full file names to server:filename mappings. 
 

####Setting up:
 
 1. Create file file1: Client calls File server to create file. File server returns with the file path created and the internal file name
	
    response = requests.post('http://localhost:9998/Files/file1/create', data="This is File1")
    response.json()
    {'filename': 'file1',
     'fullFilePath': 'c:\\DistFileSystem\\FilesRoot\\xnxjr6c32z',
     'internalFileName': 'xnxjr6c32z'}

 
 1. Client adds the File server to the response and posts it back to the Directory Server. In the end, the file server is only aware of the file itself (with an internal name) and the directory server is awere of the mapping:

    requests.get("http://localhost:9998/Files").text
    Out[412]: '["p4rfhgtgxj"]'
    
    requests.get("http://localhost:9998/Directory").text
    Out[413]: '{"file1": ["http://localhost:9998/", "p4rfhgtgxj"]}

 
 
		
1) Client want to open file1
	1.1) ask the directory server where it is located