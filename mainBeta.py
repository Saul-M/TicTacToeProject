import asyncio
import json
from websockets.server import serve

# Stores a list of users
listOfUsers = []
userDictionary = {}
# Stores all clients
allConnections = set()

async def serverHandler(websocket):
    # Adds new connection to client list
    # allConnections.add(websocket)

    try:
        async for msg in websocket:
            await msgHandler(websocket, msg)
    finally:
        # Removes connection and their ID from stored listOfUsers
        if websocket in allConnections:
            # Get their ID and remove their websocket and from list
            idVal = id(websocket)
            allConnections.remove(websocket);

            if(listOfUsers.count != 0):
                if idVal in listOfUsers:
                    listOfUsers.remove(idVal)

            for connected in allConnections:
                await connected.send(json.dumps({'type' : 'remove', 'data' : idVal}))



async def msgHandler(websocket, msg):

    msg_information = json.loads(msg)
    msg_type = msg_information.get('type')

    print(msg_type)   
    if (msg_type == 'joinOnline'):
        await addUser(websocket)
    elif (msg_type == 'request'):
        await gameReq(websocket, msg_information)
    elif (msg_type == 'gameAccepted'):
        await gameAccpt(websocket, msg_information)
    elif (msg_type == 'beginMatch'):
        await beginMatch(websocket)

async def gameReq(websocket, msg_inf):
    sentID = id(websocket);

    oppID = msg_inf.get('id')
    print(oppID)
    opponentWS = userDictionary[oppID]
    print(opponentWS)
    await opponentWS.send(json.dumps({'type':'GameReq', 'id': sentID}))

async def gameAccpt(websocket, msg_inf):
    originalSenderID = msg_inf.get('id');

    origWS = userDictionary[originalSenderID]
    await origWS.send(json.dumps({'type':'acceptedMatch'}))


async def addUser(websocket):
    # If that value does not exist in list of users, append
    if((id(websocket) not in listOfUsers)):
        # appoint the id value to that user
        allConnections.add(websocket)
        userDictionary[id(websocket)] = websocket

        listOfUsers.append(id(websocket))
        for connection in allConnections:
            await connection.send(json.dumps({'type': 'selfID', 'data':id(websocket)}))
            await connection.send(json.dumps({'type': 'array_data', 'data':listOfUsers}))




#Game State
gameState = {
    #The game starts with X
    'currentPlayer' : 'X',
    "playerWon" : False,
    #We will keep track of the moves of each player
    "p1Moves" : [],
    "p2Moves" : [],
    #The connections havent been made yet, so for now its just None
    "connections" : {"p1":None, "p2":None}

}
#Game Board that we will use to check if someone won
winConditions = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
    [1, 5, 9],
    [3, 5, 7]
]

#Check if the player won Function
def checkWin(pMoves):
    for condition in winConditions:
        if(all(elem in pMoves for elem in condition)):
            return True
    return False

async def place_mark(websocket, cell_id):
    #player identification 
    current_player_id = 'p1' if gameState['currentPlayer'] == 'X' else 'p2'
    if websocket != gameState['connections'][current_player_id]:
        # It's not this player's turn
        await websocket.send(json.dumps({'type': 'error', 'message': "It's not your turn"}))
        return

    if gameState['playerWon']:
        # Game is already won, no more moves allowed
        await websocket.send(json.dumps({'type': 'error', 'message': 'Game over'}))
        return

    #here it just checks if the cell id is valid, if not it will send an error
    try:
        cell_id = int(cell_id)
    except ValueError:
        await websocket.send(json.dumps({'type': 'error', 'message': 'Invalid cell ID'}))
        return

    spots = gameState['p1Moves'] if gameState['currentPlayer'] == 'X' else gameState['p2Moves']
    if cell_id not in spots and cell_id not in gameState['p1Moves'] and cell_id not in gameState['p2Moves']:
        spots.append(cell_id)
        gameState['playerWon'] = checkWin(spots)

        if gameState['playerWon']:
            # When a player wins, send the winning state and reset the game
            await broadcast({'type': 'win', 'player': gameState['currentPlayer']})
            #reset_game_state()  # Reset the game state for a new game
        else:
            # Toggle the current player
            gameState['currentPlayer'] = 'O' if gameState['currentPlayer'] == 'X' else 'X'
            # Create a serializable game state to send
            serializable_state = {
                'currentPlayer': gameState['currentPlayer'],
                'playerWon': gameState['playerWon'],
                'p1Moves': gameState['p1Moves'],
                'p2Moves': gameState['p2Moves']
            }
            # Send the new serializable state to both players
            await broadcast({'type': 'state', 'state': serializable_state})




async def broadcast(message):
    # Create a new dict that doesn't include the WebSocketServerProtocol objects
    message_to_send = json.dumps(message)
    
    for player in gameState['connections']:
        if gameState['connections'][player]:
            # Send the JSON serialized message
            await gameState['connections'][player].send(message_to_send)
    # Inside your place_mark function, before calling broadcast



async def beginMatch(websocket):
    #we have to assign the players to the connections
    player = 'p1' if gameState['connections']['p1'] == None else 'p2'
    gameState['connections'][player] = websocket
    await websocket.send(json.dumps({'type': 'player', 'player':player}))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if "cellId" in data:
                await place_mark(websocket, data['cellId'])
    
    finally:
        gameState['connections'][player] = None
        gameState['playerWon'] = False
        gameState['p1Moves'] = []
        gameState['p2Moves'] = []
        gameState['currentPlayer'] = 'X'
        print("Connection Closed")

# start_server = websockets.serve(serverHandler, "0.0.0.0", 65432)
async def main():
    async with serve(serverHandler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

# asyncio.run(main())




asyncio.run(main())
