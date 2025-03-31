window.paneer = {
    _promises: new Map(),

    invoke: (func, args) => {
        const id = Date.now() +  Math.random().toString(36).substring(2, 11);
        return new Promise((resolve, reject) => {
            try {
                window.webkit.messageHandlers.paneer.postMessage({ id, func, args });
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