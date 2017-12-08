# Scalable Computing

### <i class="icon-file"></i> Project 3 - Distributed File System:

[Please read the report located here](DistFileSystem/report.pdf)

	

#### <i class="icon-file"></i> Project 2 - Ciclo Complexity:

* Assumptions:

1) Both, server and each client, will have a copy of the repo. I want to avoid adding the network transmission time and focus on the time it takes to do the calculation
2) All relevant information should be read from the GlobalConfig file
3) Server will start, dowload the repo into the "CycloServer" folder and stay on a "not ready" state until told otherwise. This is to make sure all clients get to work at the same time.
4) Start as many clients as needed. Each one will download the repo and start asking the server for work. Server will respond "not ready"
5) Make "get" server call to "/ready". This will make the server start handling out jobs.
6) Once there are no more jobs. Clients die and server outputs final final on the fomart: "{UnIdentifier}{RepoName}_{nClients}Clients.csv'


Results on the DLTK repo 

![ResultsDLTK](/CyclomaticComplx/Results/DLTK.png)


#### <i class="icon-file"></i> Project 1 - Chat Server:
```
// Running:
python ChatServer.py --host localhost --port 1234
```

or (Unix only):

```
start.sh --host=<host ip> --port=<port>
```