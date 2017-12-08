# Scalable Computing

### <i class="icon-file"></i> Project 3 - Distributed File System:

[Please read the report located here](DistFileSystem/Report.pdf)




### <i class="icon-file"></i> Project 2 - Ciclo Complexity:


This project consists in constructing a REST service system, focussed on the efficient computation of code complexity for a given repository, utilising a set of nodes as appropriate to minimise execution time from submission to result return.


* Assumptions:

1) Both, server and each client, will have a copy of the repo. I want to avoid adding up the network transmission time and focus on the time it takes to do the calculation
2) Config information (local working directory, repository URL and the Cyclo Server Adress) are being read from the GlobalConfig file

* How to run:

1) Start the server by running ```CycloServer.py```
2) Server will dowload the repo into the "CycloServer" folder (on the working directory) and stay on a "not ready" state until told otherwise. This is to make sure all clients get to work at the same time.
3) Start as many clients as needed by running ```CycloClient.py```. Each one will download the repo and start asking the server for work. Server will respond "not ready"
4) Make "get" server call to ```"{serverURL}/ready"```. This will make the server start handing out jobs.
5) Once there are no more jobs. Clients die and server outputs final final on the fomart: "{UnIdentifier}{RepoName}_{nClients}Clients.csv'


Results on the DLTK repo. As we can see the total time goes down with the number of workers until a certain point where the server becomes the bottleneck

![ResultsDLTK](/CyclomaticComplx/Results/DLTK.png)




### <i class="icon-file"></i> Project 1 - Chat Server:
```
// Running:
python ChatServer.py --host localhost --port 1234
```

or (Unix only):

```
start.sh --host=<host ip> --port=<port>
```