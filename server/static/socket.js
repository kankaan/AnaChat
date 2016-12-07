    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
		console.log("connected to server")
        socket.emit('JSONMessage', {"message": 'I\'m connected!'});
    });
	socket.emit("JSONMessage",{"message":"hej"})

function sendMessage() {
	var message = document.getElementById('chatMessage').value;
	socket.emit("JSONMessage",{"message":message})
}

socket.on("receivedMessage", function(_message) {
	var chatList =  document.getElementById("chatMessagesList");
    var receivedMessage = document.createElement("li");
    var node = document.createTextNode(_message);
    receivedMessage.appendChild(node);
    receivedMessage.className = "list-group-item"
    chatList.appendChild(receivedMessage);
    console.log(_message);
	$("#chatMessageList").animate({ scrollTop: $("#chatMessageList")[0].scrollHeight }, 1000);
});

