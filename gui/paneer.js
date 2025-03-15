window.paneer = {
    invoke: (func, args) => new Promise((resolve, reject) => {
        try {
            window.webkit.messageHandlers.paneer.postMessage({ func, args });
            window.paneer._resolve = resolve;
        } catch (error) {
            reject(error);
        }
    }),
    _resolve: () => {}
};