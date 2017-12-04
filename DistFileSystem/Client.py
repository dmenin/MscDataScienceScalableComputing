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
response = requests.post('http://localhost:9998/Files/file1/create', data="This is File1")
response.json()

mapper = {}
mapper[2] =2



