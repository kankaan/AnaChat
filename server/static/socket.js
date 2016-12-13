// Create websocket connection:
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
		console.log("connected to server");
		joinToRoom()
});

// This is called when the user pushes 'send' button
// Application utilizes hidden html fields for storing the information, like
// ChatID.
function sendMessage() {
	var chatID = document.getElementById("currentChatID").value;
	var message = document.getElementById('chatMessage').value;
	socket.emit("JSONMessage",{"message":message, "room":chatID})
    // When the message is sent, remove the message from the text field
    document.getElementById('chatMessage').value = "";
}

// websocket listener:
// Function pushes the messages to the chat. Every message is an list element.
socket.on("receivedMessage", function(_message) {
	var chatList =  document.getElementById("chatMessagesList");
    var receivedMessage = document.createElement("li");
    var node = document.createTextNode(_message);
    receivedMessage.appendChild(node);
    receivedMessage.className = "list-group-item"
    chatList.appendChild(receivedMessage);
    console.log(_message);
});

function joinToRoom() {
	var chatID = document.getElementById("currentChatID").value;
	console.log(chatID)
	socket.emit("join",{"room":chatID});
}

// TODO: changes the chat title to respond the chat's title
function setTitle() {
	document.getElementById("chatTopic").innerHTML = "testi";
}
setTitle();

// TODO: create a feature to changes the chat focus to the newest message.
// When it is done, create button to enable and disable the feature.
//$('li').last().addClass('active-li').focus();
