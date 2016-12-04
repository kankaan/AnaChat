var app = new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue!'
  }
})

function sendMessage() {
//$.post( "/chatti", {})
var message = document.getElementById('chatMessage').value;
var token = document.getElementById('csrf_token').value;
console.log(message);
console.log(token);
$.post( "/chatti", {"message":message, "csrf_token":token})
}
