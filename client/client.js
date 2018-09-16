var socket = require('socket.io-client')('http://localhost:5000');

socket.on('connect', () => {
    console.log('connect');
    socket.emit('exa_subscribe', { 'prefixes': [ '0.0.0.0/0' ] });
});

socket.on('disconnect', () => {
    console.log('you have been disconnected');
});

socket.on('exa_message', function(msg) {
    console.log(msg);
});


// socket.emit('disconnect');
