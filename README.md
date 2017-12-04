# Scalable Computing

### <i class="icon-file"></i> Project 3 - Distributed File System:

#### Assumptions:

* For the sake of simplicity, same Server can perform more than one role
* Directory\File Server: store all files in a file server in a flat file system (i.e. each file server provides a single directory in effect), requiring the directory server to maintain mapping of full file names to server:filename mappings. 
 

#### Setting up:
 
 1. Create 5 files: Client calls File server to create files. File server returns with the file path created and the internal file name
	
	```
    response = requests.post('http://localhost:9998/Files/file1/create', data="This is File1")
    response.json()
    {'filename': 'file1',
     'fullFilePath': 'c:\\DistFileSystem\\FilesRoot\\xnxjr6c32z',
     'internalFileName': 'xnxjr6c32z'}
	 ```

 
 1. Client adds the File server to the response and posts it back to the Directory Server. Objective is that the file server is only aware of the files themselves (with an internal name) and the directory server is aware of the mapping:
	
	```
	requests.get("{}/Files".format(file_server)).json()
	Out[1016]: ['8sgfrhqrz1', 'lhzptqb766', 'tjwiu1ulix', 'tsvxsglrd2', 'tzrexc21b6']
	
	requests.get("{}/Directory".format(directory_server)).json()
	Out[1017]: 
	{'file0': ['http://localhost:9998', 'tjwiu1ulix'],
	 'file1': ['http://localhost:9998', 'tsvxsglrd2'],
	 'file2': ['http://localhost:9998', 'tzrexc21b6'],
	 'file3': ['http://localhost:9998', '8sgfrhqrz1'],
	 'file4': ['http://localhost:9998', 'lhzptqb766']}
 	 ```
 
	
#### Running Client:

	1. Client.py does a few scripted tasks to test all actions

		* Gets list of files from directory server and chooses one at random
		* Asks the directory server where the file is and what it is internally called:
		* Returns File Server API and Internal File name
		* Checks Local Cache if file exists (Wont have it)`
		* Asks the locking server if file is available (it will be)
		* Request a Lock (receives an OK)
		* Simulate another client asking for the lock - anything different than OK mean the lock cant be granted
		* Asks the file server for the file, creates a local copy and change it
		* Posts it back to the file server - no need to interact with Directory server at this stage anymore
		* Adds file to the local cache
		* Release the lock:


	2. Test Caching on Client1 - should not fetch the same file twice:
		
		* Request same file
		* Check the local cache - File exists and matches the server (md5 check)
		* Updates cached version - posts back to the server
		
		
	3. Second Client Updates the same file
	
		* Set up client2
		* Client 2 does not have file on cache
		* Client2 request file from server and changes it
		* Update client2 cache

	4. Client1 requests same file
		
		* File exists on Client1's cache but its obsolete.
		* Cache is deleted
		* Client 1 requests file from server again
		* Changes and pushes it

	

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



	```

 
 
		
1) Client want to open file1
	1.1) ask the directory server where it is located