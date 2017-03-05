var express = require('express');
var app = express()
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use("/", express.static(__dirname + '/public'));

io.on('connection', function(socket){
  socket.on('old_page', function(msg){
    io.emit('old_page', msg);
  });
  socket.on('terms', function(msg){
    io.emit('terms', msg);
  });
  socket.on('new_page', function(msg){
    io.emit('new_page', msg);
  });
  socket.on('google_search', function(msg){
    io.emit('google_search', msg);
  });
  socket.on('social_media', function(msg){
    io.emit('social_media', msg);
  });
  socket.on('dark_search', function(msg){
    io.emit('dark_search', msg);
  });
  socket.on('export', function(msg){
    console.log("Export!!");
    io.emit('export', msg);
  });
  socket.on('prompt', function(msg){
    console.log("Prompt!!");
    io.emit('prompt', msg);
  });
  socket.on('google_link', function(msg){
    console.log("here!")
    console.log(msg);
    io.emit('google_link', msg);
  });

});

var port = 3000;

http.listen(port, function(){
  console.log('listening on ' + port);
});