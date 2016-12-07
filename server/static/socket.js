var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
		console.log("connected to server");
		joinToRoom()
});

function sendMessage() {

	var chatID = document.getElementById("currentChatID").value;
	var message = document.getElementById('chatMessage').value;
	socket.emit("JSONMessage",{"message":message, "room":chatID})
    document.getElementById('chatMessage').value = "";
}

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

function setTitle() {
	document.getElementById("chatTopic").innerHTML = "testi";
}
setTitle();
