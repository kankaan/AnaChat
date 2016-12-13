// Create a new chat by sending post message to the server
// TODO: Validate information before sending to the server
function newChat() {
var name = document.getElementById("chatName").value;
var title = document.getElementById("chatTitle").value;
var token = document.getElementById('csrf_token').value;
console.log(name)
console.log(title)
$.post( "/newChat", {"chatName":name,"chatTitle":title, "csrf_token":token})
$('#createChatModal').modal('hide')
}

// This function should be used to loading a existing chats.
function queryChat() {
	var token = document.getElementById('csrf_token').value;
	$.post("/chatList",{"csrf_token":token})
}

$('#joinChat').click(function () {
	var token = document.getElementById('csrf_token').value;
	var chatList = $.post("/chatList",{"csrf_token":token}).done(
		function( data ) {
			console.log(data);
		});
	    $('#modal-content').modal({
        show: true
    });
});

function gotoChat(chatID) {
	var token = document.getElementById('csrf_token').value;
	$.post("/chat",{"csrf_token":token});
}
