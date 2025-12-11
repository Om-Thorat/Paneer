window.paneer = {
    _promises: new Map(),

    invoke: (func, args) => {
        const id = Date.now() +  Math.random().toString(36).substring(2, 5);
        console.log(id.length,id);
        return new Promise((resolve, reject) => {
            try {
                const payload = { id, func, args };
                if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.paneer) {
                    window.webkit.messageHandlers.paneer.postMessage(payload);
                } else if (window.chrome && window.chrome.webview) {
                    window.chrome.webview.postMessage(JSON.stringify(payload));
                } else {
                    console.warn("Paneer backend not detected.");
                }
                window.paneer._promises.set(id, resolve);
            } catch (error) {
                reject(error);
            }
        });
    },

    _resolve: ({id, result}) => {
        const resolve = window.paneer._promises.get(id);
        if (resolve) {
            resolve(result);
            window.paneer._promises.delete(id);
        }
    }
    
};