var express = require('express');
var app = express()
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use("/", express.static(__dirname + '/public'));

io.on('connection', function(socket){
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
    io.emit('export', msg);
  });
  socket.on('prompt', function(msg){
    io.emit('prompt', msg);
  });
  socket.on('google_link', function(msg){
    io.emit('google_link', msg);
  });
  socket.on('page_update', function(msg){
    io.emit('page_update', msg);
  });

});

var port = 3000;

http.listen(port, function(){
  console.log('listening on ' + port);
});