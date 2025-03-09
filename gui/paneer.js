const socket = new WebSocket("ws://localhost:8765");

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data,"heyooo");
    if (data.id && responseHandlers[data.id]) {
        responseHandlers[data.id](data.res);
        delete responseHandlers[data.id];
    }
};

socket.onerror = function(error) {
    document.getElementById('output').innerText = 'Error: ' + error.message;
};

const responseHandlers = {};

function generateUniqueId() {
    return '_' + Math.random().toString(36).substring(2, 11);
}

function paneerInvoke(action, args) {
    return new Promise((resolve, reject) => {
        const id = generateUniqueId();
        responseHandlers[id] = resolve;
        try {
            console.log("sending.....")
            socket.send(JSON.stringify({ action, id, ...args }));
        } catch (error) {
            reject('Error: ' + error);
        }
    });
}
