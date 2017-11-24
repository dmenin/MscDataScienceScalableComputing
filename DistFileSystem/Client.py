import requests

#get list of files
response = requests.get("http://localhost:9998/Files")
print (response.text)

requests.get("http://localhost:8000/states")


response = requests.get("http://localhost:8888")
print (response.text)
msg = response.text + 'done!'

response = requests.post('http://localhost:8888', data='{}'.format(msg))



things_to_do = ['task1', 'task2', 'task3']

len(things_to_do )
things_to_do.pop(0)


#Create a file
response = requests.post('http://localhost:9998/Files/foobar/create', data="AAAAAA")


CycloServerAdress = "http://localhost:8888"
while True:
    response = requests.get(CycloServerAdress)

    task = response.text
    if task == '"Done"': #deal with the double quotes
        break
    msg = response.text + 'done!'
    response = requests.post('http://localhost:8888', data='{}'.format(msg))
    
    
    
a='aaaa'
a