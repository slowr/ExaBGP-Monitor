var io = require('socket.io')();

io.on('connection', (client) => {
    console.log('connect');

    client.on('disconnect', () => {
        console.log('disconnect');
    });

    client.on('exa_subscribe', (msg) => {
        console.log(msg);
        client.emit('exa_message', 'hi');
    });

    client.emit('ris_rcc_list', 'hi');

});

io.listen(5000);
