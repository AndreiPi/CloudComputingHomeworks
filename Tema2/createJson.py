import json

f = open("animals","r")
d=dict()
d= json.load(open("animals2.json","r"))
#print(d["Black Rhinoceros"]['Diet'])
js = open("animals2.json","w")
line = f.readline()
name=line.strip(' \t\n')
animal = dict()
line = f.readline()
while(line):
    k = line.split(':')[0]
    v = line.split(':')[1].strip(' \t\n')
    animal[k]=v
    line = f.readline()
d[name]=animal
json.dump(d,js,indent=2)