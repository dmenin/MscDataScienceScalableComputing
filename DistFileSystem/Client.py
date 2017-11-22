import requests

#get list of files
response = requests.get("http://localhost:9998/Files")
print (response.text)

#Create a file
response = requests.post('http://localhost:9998/Files/foobar/create', data="AAAAAA")