
function newChat() {
console.log("foo")
var name = document.getElementById("chatName").value;
var title = document.getElementById("chatTitle").value;
var token = document.getElementById('csrf_token').value;
console.log(name)
console.log(title)
$.post( "/newChat", {"chatName":name,"chatTitle":title, "csrf_token":token})

}

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
