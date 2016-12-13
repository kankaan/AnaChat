// This was the first try to utilize server sent events.


function sendMessage() {
var message = document.getElementById('chatMessage').value;
var token = document.getElementById('csrf_token').value;
console.log(message);
console.log(token);
$.post( "/chatMessage", {"message":message, "csrf_token":token})
}

if(typeof(EventSource) !== "undefined") {
    var source = new EventSource("/chatStream");
    source.onmessage = function(event) {
        var chatList =  document.getElementById("chatMessagesList");

		var receivedMessage = document.createElement("li");
		var node = document.createTextNode(event.data);
		receivedMessage.appendChild(node);
		receivedMessage.className = "list-group-item"
		chatList.appendChild(receivedMessage);
		console.log(event.data);
    };
} else {
    document.getElementById("result").innerHTML = "Sorry, your browser does not support server-sent events...";
}

