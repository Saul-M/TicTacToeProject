// REPLACE THE ws://##### WITH IP ADDRESS FROM THE MACHINE THE SERVER
// IS RUNNING FROM
const ws = new WebSocket("ws://67.187.176.118:8765");
//const ws = new WebSocket("ws://10.0.0.132:8765");

// If the client is able to connect
ws.addEventListener("open", () => {
    console.log("Client was able to Connect");
    // Sends the msg to the server
});

// Listen for any messages from the client
/*
ws.addEventListener("message", (event) => {
    console.log(event);

    if(event.type == 'remove')
    {
        console.log("REMOVAL");
        removeUser(event.data);
    }
    else
    {
        displayUsers(event.data);
    }
    //createUser(event.data);
});
*/
ws.onmessage = function(event)
{
    let recData = JSON.parse(event.data)
    if(recData.type == 'remove')
    {
        console.log('REMOVAL');
        removeUser(event.data)
    }
    else if(recData.type == 'array_data')
    {
        displayUsers(event.data);
    }
    else if(recData.type == 'selfID')
    {
        selfAppoint(event.data);
    }
    else if(recData.type == 'GameReq')
    {
        console.log("abc");
        recievedGameReq(event.data);
    }
    else if(recData.type == 'acceptedMatch')
    {
        gameAccepted();
    }
}

var selfID;
var listOfUsers = [];


function selfAppoint(data)
{
    let onlineButtonDiv = document.getElementById("buttonMenu");

    onlineButtonDiv.remove();

    let id = (JSON.parse(data)).data;

    selfID = id;

    let selfDisplay = document.createElement("div");
    selfDisplay.id = "self";
    document.body.appendChild(selfDisplay);

    listOfUsers.push(selfID);
    let userDiv = document.getElementById("self");
                
    let disp = document.createElement("p");
    disp.textContent = "Welcome User #" + id;

    userDiv.appendChild(disp);

    let requestLists = document.createElement("li");
    requestLists.id = "requestList";

    userDiv.appendChild(requestLists);
}

// Displays the users connected
function displayUsers(data)
{
    // Parses the data into an array 
    if(!(document.getElementById("playerList")))
    {
        let pList = document.createElement("div");
        pList.id = "playerList";
        document.body.appendChild(pList);
    }
    let players = document.getElementById("playerList");
    let serverUser = (JSON.parse(data)).data;

    for(let i = 0; i < serverUser.length; i++)
    {
        // If the user does exist in the listOfUsers array
        if(listOfUsers.find(item => item === serverUser[i]))
        {
            console.log("EXIST: " + i);

        }
        // Else, create a new user
        else
        {
            console.log("NO EXIST: " + i);
            createUser(serverUser[i], players);
        }
    }

}

function removeUser(data)
{
    userID = (JSON.parse(data)).data;
    console.log(userID);
    let userDisplay = document.getElementById("ID" + userID);
    userDisplay.remove();
}

// Creates a new user
function createUser(id, pDisplay)
{
    console.log(id);
    // If its the client's id, dont display it on html
        // Add it to the list of users
    listOfUsers.push(id);
    let userDiv = document.createElement("div");
    userDiv.className = "playerOnline";
    userDiv.id = "ID" + id;
                
    let disp = document.createElement("p");
    disp.textContent = "User #" + id;

    pDisplay.appendChild(userDiv);

    let connectButton = document.createElement("input");
    connectButton.type = "button";
    connectButton.className = "OnlineRequestButton";
    connectButton.value = "Click to Game Request!";
    connectButton.onclick = function() {
        sendGameRequest(id);
    };
    userDiv.appendChild(disp);
    userDiv.appendChild(connectButton)

}

function sendGameRequest(idNum)
{
    let gameReq = JSON.stringify({type:"request", id: idNum});
    ws.send(gameReq);
}

function recievedGameReq(data)
{
    userID = (JSON.parse(data)).id;

    let list = document.getElementById("requestList");

    let newRequest = document.createElement("ul");
    newRequest.id = "Request:" + userID;

    let options = document.createElement("div");
    
    let label = document.createElement("label");
    label.textContent = "Accept game from user: " + userID + "?";
    
    let accept = document.createElement("input");
    accept.type = "button";
    accept.value = "Accept";
    accept.onclick = function() {
        newRequest.remove();
        ws.send(JSON.stringify({type:"gameAccepted", id:userID}))
        window.location.href = "test.html";

    };

    let deny = document.createElement("input");
    deny.type = "button";
    deny.value = "Reject";
    deny.onclick = function() {
        newRequest.remove();
    };

    options.appendChild(label);
    options.appendChild(accept);
    options.appendChild(deny);

    newRequest.appendChild(options);
    list.appendChild(newRequest);

}

function gameAccepted()
{
    window.location.href = "test.html"; 
}

// Sends the id to the server
function sendID()
{
    // Sends id to server and appoints itself as a selfID
    // For easier identification
    let sendID_data = JSON.stringify({type: "joinOnline"});
    ws.send(sendID_data);
}

