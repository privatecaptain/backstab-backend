from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import json
import ast
 
filename = "data.json"
gameList = []


def readjson():
    x = open(filename,"r+")
    destination = ast.literal_eval(x.read())
    x.close()
    return destination

def checkgame():
    database = readjson()
    return database["status"]

def changestatus():
    x = open(filename,"r+")
    database = ast.literal_eval(x.read())
    if database["status"] == "True":
        database["status"] = "False"
    else:
        database["status"] = "True"
    x.seek(0)
    x.write(json.dumps(database))
    x.truncate()
    x.close()


def update_gps_coordinates(id,coordinates):
    x = open(filename,"r+")
    players = ast.literal_eval(x.read())
    players[id]["co-ordinates"] = coordinates
    x.seek(0)
    x.write(json.dumps(players))
    x.truncate()
    x.close()

def createnewplayer(newplayer,id):
    x = open(filename,"r+")
    destination = ast.literal_eval(x.read())
    destination[id] = newplayer
    x.seek(0)
    x.write(json.dumps(destination))
    x.truncate()
    x.close()

def killplayer(id):
    x = open(filename,"r+")
    destination = ast.literal_eval(x.read())
    if id in destination:
        temp_target = destination[destination[id]["target_id"]]["target_id"]
        destination.pop(destination[id]["target_id"],None)
        destination[id]["target_id"] = temp_target
    x.seek(0)
    x.write(json.dumps(destination))
    x.truncate()
    x.close()

def startgame():
    x = open(filename,"r+")
    destination = ast.literal_eval(x.read())
    gameList = destination.keys()
    if "status" in gameList:
        gameList.remove("status")
    for i in range(0,len(gameList)-1):
        destination[gameList[i]]["target_id"] = gameList[i+1]
    temp = gameList[-1]
    destination[temp]["target_id"] = gameList[0]
    destination["status"] = "True"
    x.seek(0)
    x.write(json.dumps(destination))
    x.truncate()
    x.close()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        response = readjson()
        if len(response) < 10:
            self.write("Only "+str(len(response))+" people on the server , so yeah no game :(")
            self.write(response)
        else:
            self.write('Game On!!!')
        

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = { 'version': '3.5.1',
                     'last_build':  date.today().isoformat() }
        self.write(response)
 
class GetPlayerByIdHandler(tornado.web.RequestHandler):
    def get(self, id):
        players = readjson()
        response = players[id]
        self.write(response)


class CreateNewPlayerHandler(tornado.web.RequestHandler):
    def get(self,name,major,year,id,coordinates):
        newplayer = {"name" : name,
                    "Major" : major,
                    "co-ordinates" : coordinates,
                    "year" : year,
                    "target_id":""
                     }
        if checkgame() == 'False': #Remeber to making something for double registration
            createnewplayer(newplayer,id)
            self.write('Player Created!!')
        else:
            self.write('Sorry Game Already Started.')


class UpdateCoordinatesById(tornado.web.RequestHandler):
    def get(self,id,latitude,longitude):
        coordinates = (latitude,longitude)
        update_gps_coordinates(id,coordinates)
        self.write('GPS Co-ordinates Updated.')

class KillPlayerById(tornado.web.RequestHandler):
    def get(self,id):
        if checkgame() == "True":
            killplayer(id)
            self.write('Player Killed!!')
        else:
            self.write('Not so soon..')

class StartGameHandler(tornado.web.RequestHandler):
    def  get(self):
        startgame()
        self.write("Game Started Enjoy!!!")

class StopGameHandler(tornado.web.RequestHandler):
    def get(self):
        changestatus()
        self.write("Game Ended !!")


application = tornado.web.Application([
    (r"/",MainHandler),
    (r"/getplayerbyId/([0-9]+)", GetPlayerByIdHandler),
    (r"/version", VersionHandler),
    (r"/createnewplayer/@Name=([\w]+)&Major=([\w]+)&Year=(\d)&Id=([\d]+)&Coordinates=([-]*[\d]+.[\d]+,[-]*[\d]+.[\d]+)",CreateNewPlayerHandler),
    (r"/updatecoordinates/([0-9]+)/@([-]*[0-9]+.[0-9]+),([-]*[0-9]+.[0-9]+)",UpdateCoordinatesById),
    (r"/killplayer/([0-9]+)",KillPlayerById),
    (r"/startgame@backstabadmin",StartGameHandler),
    (r"/stopgame",StopGameHandler)
])
 
print "Server Running..."
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
print "Server Running..."
