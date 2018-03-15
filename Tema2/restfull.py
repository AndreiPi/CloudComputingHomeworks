import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import re
import json

animalsData = json.load(open("animals.json", 'rb'))
resources = ["endageranimals"]

hostName = "localhost"
hostPort = 8000


def ParameterOptionsIntersect():
    s = set()
    for e in animalsData:
        sp = set()
        for p in animalsData[e]:
            sp.add(p.lower())
        if len(s) == 0:
            s = sp
        else:
            s = s.intersection(sp)
    return s

def ParameterOptionsAll():
    s = set()
    for e in animalsData:
        for p in animalsData[e]:
            s.add(p.lower())
    return s


class MyServer(BaseHTTPRequestHandler):

    #	GET is for clients geting the predi

    def Element_Get(self, item):
        d = dict()
        for i in animalsData:
            if i.lower() == item.lower():
                d = animalsData[i]
        if len(d)==0:
            self.send_response(404)
            self.end_headers()
            return -1

        self.send_response(200)  # create header
        self.send_header("Content-Length", str(len(str(json.dumps(d)))))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode("utf-8"))
        self.wfile.flush()
        return 1
    def Element_GetFilter(self, item,parameters):
        d = dict()
        animal=dict()
        for i in animalsData:
            if i.lower() == item.lower():
                animal = animalsData[i]
        for p in parameters:
            pName = [i for i in animal.keys() if i.lower() == p[0].lower()]
            if len(pName) > 0:
                p[0]=pName[0]
                d[p[0]]=animal[p[0]]
        if len(d)==0:
            self.send_response(404)
            self.end_headers()
            return -1

        self.send_response(200)  # create header
        self.send_header("Content-Length", str(len(json.dumps(d))))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode("utf-8"))
        self.wfile.flush()
        return 1

    def Collection_GetAll(self):
        d = dict()
        for e in animalsData:
            uri = '/'.join([hostName + ':' + str(hostPort), self.collectionName]) + '/' + "+".join(e.split(' '))
            d[e] = uri

        self.send_response(200)  # create header
        self.send_header("Content-Length", str(len(str(json.dumps(d)))))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode("utf-8"))
        self.wfile.flush()

    def Collection_GetFiltred(self, parameters):
        d = dict()

        for e in animalsData:
            ok = True
            for p in parameters:
                pName = [i for i in animalsData[e].keys() if i.lower() == p[0].lower()]
                if len(pName) == 0:
                    ok = False
                else:
                    p[0] = pName[0]

                    if p[1].lower() != animalsData[e][p[0]].lower():
                        ok = False
            if ok:
                uri = '/'.join([hostName + ':' + str(hostPort), self.collectionName]) + '/' + "+".join(e.split(' '))
                d[e] = uri

        self.send_response(200)  # create header
        self.send_header("Content-Length", str(len(str(json.dumps(d)))))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode("utf-8"))
        self.wfile.flush()

    def do_GET(self):
        path = re.split(r"/", self.path)
        path = [i for i in path if i]
        if len(path) == 0 or len(path) > 2:
            self.send_response(400)
            self.end_headers()
            return -1
        if path[0].lower() in resources:
            self.collectionName = path[0]
            if len(path) == 1:
                self.Collection_GetAll()
                return 1
            else:
                item = path[1].replace('+', ' ')
                e = path[-1]
                if e[0] == '?':
                    parameters = e[1:].split('&')
                    validParameters = []
                    # print(parameters)
                    for p in parameters:
                        if p.count('=') != 1:
                            self.send_error(400, 'Bad request')
                            self.end_headers()
                            return -1
                        splitParam = p.replace('+', ' ').split('=')
                        print(splitParam)
                        if splitParam[0].lower() in parametersSet:
                            validParameters.append(splitParam)
                            # self.Collection_GetFiltred(splitParam[0],splitParam[1])
                        else:
                            self.send_error(400, "Bad request - parameter doesn't exist")
                            self.end_headers()
                            return -1
                    self.Collection_GetFiltred(validParameters)
                    return 1
                else:
                    return self.Element_Get(item)
        else:
            self.send_error(404)
            self.end_headers()
            return -1

    def Collection_PutAll(self,data):
        try:
            d= json.loads(data)
        except Exception as e:
            self.send_error(400,"Bad request - Collection in wrong format")
            self.end_headers()
            return -1
        #print(d)
        json.dump(d,open("animals.json","w"))
        global animalsData
        global parametersSet
        animalsData = json.load(open("animals.json", 'rb'))
        parametersSet = ParameterOptionsAll()
        self.send_response(200,"OK")
        self.end_headers()
        return 1

    def Element_Put(self,item,data):
        for k in animalsData:
            if k.lower()==item.lower():
                try:
                    value= json.loads(data)
                except :
                    self.send_error(400, "Bad request - Item in wrong format")
                    self.end_headers()
                    return -1
                animalsData[k]=value
                json.dump(animalsData,open("animals.json","w"))
                self.send_response(200, "OK")
                self.end_headers()
                return 1
        try:
            value = json.loads(data)
        except:
            self.send_error(400, "Bad request - Item in wrong format")
            self.end_headers()
            return -1
        animalsData[item] = value
        json.dump(animalsData, open("animals.json", "w"))
        self.send_response(200, "OK")
        self.end_headers()
        return 1


    def do_PUT(self):
        path = re.split(r"/", self.path)
        path = [i for i in path if i]
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        data =  self.rfile.read(content_length).decode('utf-8')
        if len(path) == 0 or len(path) > 2:
            self.send_response(400)
            self.end_headers()
            return -1
        if path[0].lower() in resources:
            self.collectionName = path[0]
            if len(path) == 1:
                #print(data)
                return self.Collection_PutAll(data)
            else:
                return self.Element_Put(path[1],data)
        self.send_error(400, "Bad request - Item in wrong format")
        self.end_headers()
        return -1

    def Element_Post(self,item,data):
        for k in animalsData:
            if k.lower()==item.lower():
                try:
                    value= json.loads(data)
                except :
                    self.send_error(400, "Bad request - Item in wrong format")
                    self.end_headers()
                    return -1
                animalsData[k]=value
                json.dump(animalsData,open("animals.json","w"))
                self.send_response(200, "OK")
                self.end_headers()
                return 1
        try:
            value = json.loads(data)
        except Exception as e:
            self.send_error(400, "Bad request - Item in wrong format")
            self.end_headers()
            return -1
        d=dict()
        d[item]='/'.join([hostName + ':' + str(hostPort), self.collectionName]) + '/' + "+".join(item.split(' '))
        animalsData[item] = value

        json.dump(animalsData, open("animals.json", "w"))
        self.send_response(200, "OK")
        self.send_header("Content-Length", str(len(str(json.dumps(d)))))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(d).encode("utf-8"))
        self.wfile.flush()
        return 1

    #	POST is for submitting data.
    def do_POST(self):
        path = re.split(r"/", self.path)
        path = [i for i in path if i]
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        data = self.rfile.read(content_length).decode('utf-8')
        if len(path) !=2:
            self.send_response(400, "Bad request")
            self.end_headers()
            return -1
        print(path)
        if path[0].lower() in resources:
            self.collectionName = path[0]
            return self.Element_Post(path[1], data)
        self.send_error(400, "Bad request")
        self.end_headers()
        return -1

    def Collection_Delete(self):
        try:
            open("animals.json","w").write("{}")
            global animalsData
            animalsData = dict()
        except:
            self.send_error(500, "Internal Error")
            self.end_headers()
            return -1
        self.send_response(204, "No content")
        self.end_headers()
        return 1
    def Element_Delete(self,item):
        found=""
        for k in animalsData:
            if k.lower() == item.lower():
                found = k
        if len(found)==0:
            self.send_error(404, "Not found")
            self.end_headers()
            return -1
        del animalsData[found]
        try:
            json.dump(animalsData, open("animals.json", "w"))
        except:
            self.send_error(500, "Internal Error")
            self.end_headers()
            return -1

        self.send_response(204, "No content")
        self.end_headers()
        return 1

    def do_DELETE(self):
        path = re.split(r"/", self.path)
        path = [i for i in path if i]
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        data = self.rfile.read(content_length).decode('utf-8')
        if len(path) ==0 or len(path)>2:
            self.send_response(400, "Bad request")
            self.end_headers()
            return -1
        print(path)
        if path[0].lower() in resources:
            self.collectionName = path[0]
            if len(path)==1:
                return self.Collection_Delete()
            else:
                return self.Element_Delete(path[1])

        self.send_error(400, "Bad request")
        self.end_headers()
        return -1


# import pdb; pdb.set_trace()

parametersSet = ParameterOptionsAll()
print(parametersSet)
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
