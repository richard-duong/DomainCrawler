import sys
import os

# reference to stdout and logfile
# https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting#:~:text=Just%20define%20a%20function%20that%20will%20print%20to,to%20file%20and%2For%20screen%20is%3A%20%20printing%20%28Line_to_be_printed%29

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.filename = filename 

        try:
            os.makedirs(self.filename)        
        except FileExistsError:
            pass

        count = 0
        while os.path.isfile(f"{self.filename}{count}.log"):
            count += 1
        self.filename += str(count) + ".log"
            

    def write(self, message):  
        self.terminal.write(message)
        with open(self.filename, "a") as logFile:
            logFile.write(message)

    def flush(self):
        pass  
