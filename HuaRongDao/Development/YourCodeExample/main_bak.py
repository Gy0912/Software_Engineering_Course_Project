import NetClient
import time


##Example Code For huarongdao Project
# Feel free to rewrite this file!


# This function determines whether a new message has been received
def is_received_new_message(oldTimeStamp:int, oldServerMessage:int)->bool:
    if(oldTimeStamp == zmqThread.messageTimeStamp and
    oldServerMessage == zmqThread.receivedMessage):
        return False
    else:
        return True


if __name__ == '__main__':

    ############ Connect the Server ############
    identity = "Team8"  # write your team name here.
    zmqThread = NetClient.ZmqClientThread(identity=identity)

    ############ Initialize Huarongdao System ############
    timeStamp = -1  # Used when receiving new message
    serverMessage = ""  # Used when receiving new message

    while (True):

        ############ Your Huarongdao system design ############
        ##Example just for the naive testcase
        if (is_received_new_message(timeStamp, serverMessage)):
            timeStamp = zmqThread.messageTimeStamp
            serverMessage = zmqThread.receivedMessage

            if (serverMessage == "set@9#82#112611530753044"):
                zmqThread.sendMsg("9#82#112611530753044")
                zmqThread.sendMsg("Initialization complete!")

            if (serverMessage == "move@Zu4#Down"):
                zmqThread.sendMsg("##829112611530753044")
                zmqThread.sendMsg("Valid move!")

            if (serverMessage == "move@Zu3#Left"):
                zmqThread.sendMsg("98#2#112611530753044")
                zmqThread.sendMsg("Valid move!")

            if (serverMessage == "move@Machao#Up"):
                zmqThread.sendMsg("98#2#112611530753044")
                zmqThread.sendMsg("Invalid move!")

            if (serverMessage == "move@Huangzhong#Right"):
                zmqThread.sendMsg("9#82#112611530753044")
                zmqThread.sendMsg("Invalid move!")

            if (serverMessage == "undo"):
                zmqThread.sendMsg("9#82#112611530753044")
                zmqThread.sendMsg("Undo complete!")

        time.sleep(0.01)

    '''
    For Other kinds of available serverMessage, see readMe.txt
    '''
