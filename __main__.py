from mcstatus import JavaServer
import pymongo
import datetime
import cronitor

#Fill in these variables, the cronitor api key, and the cronitor monitor key
MONGO_CLIENT_STRING = ""
DATABASE_NAME = ""
COLLECTION_NAME = ""
SERVER_IP = ""
cronitor.api_key = ""

cronitor.Monitor.put(
    key="",
    type="",
)

@cronitor.job("")
def checkwhosonline(mongo_client, db_name, collection_name):
    db = mongo_client[db_name]
    collection = db[collection_name]

    server = JavaServer.lookup(SERVER_IP)

    try:
        #Server is contactable
        status = server.status()

        if status.players.sample is not None:  # Players are online
            player_list = [player.name for player in status.players.sample]
            listof_player_dicts = [{"timestamp": datetime.datetime.utcnow().replace(second=0, microsecond=0),
                                    "player": player,
                                    "server_contactable": 1} for player in player_list]

            if len(player_list) > 1:
                collection.insert_many(listof_player_dicts)
            else:
                collection.insert_one(listof_player_dicts[0])

        else:  # No players are online
            no_players_online = {"timestamp": datetime.datetime.utcnow().replace(second=0, microsecond=0),
                                 "player": "No players online",
                                 "server_contactable": 1}
            collection.insert_one(no_players_online)
    except:
        #Server is uncontactable
        collection.insert_one({"timestamp": datetime.datetime.utcnow().replace(second=0, microsecond=0),
                               "server_contactable": 0})


def main():
    client = pymongo.MongoClient(
        MONGO_CLIENT_STRING)
    checkwhosonline(client, DATABASE_NAME, COLLECTION_NAME)

if __name__ == '__main__':
    main()
