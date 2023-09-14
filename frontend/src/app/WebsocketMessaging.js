'use client'

export default class WebsocketMessaging {
    constructor(url) {
        this.url = url;
        this.handlers = {};
        this.socket = null;
        this.shouldReconnect = false;
    }

    // Register a handler for a specific message type
    register(messageType, handler) {
        if (!this.handlers[messageType]) {
            this.handlers[messageType] = [];
        }
        this.handlers[messageType].push(handler);
    }

    // Handle incoming WebSocket messages
    handleMessage(event) {
        const data = JSON.parse(event.data);
        console.log(data);
        const messageType = data.messageType;
        if (this.handlers[messageType]) {
            this.handlers[messageType].forEach(handler => {
                handler(data);
            });
        }
    }

    // Open the WebSocket connection
    open() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        this.shouldReconnect = true;
        this.socket = new WebSocket(this.url);
        this.socket.onmessage = this.handleMessage.bind(this);

        this.socket.onopen = () => {
            console.log('WebSocket opened');
        };

        this.socket.onclose = (event) => {
            if (event.wasClean) {
                console.log('Closed cleanly');
            } else {
                console.log('Connection died');
            }

            if (this.shouldReconnect) {
                setTimeout(() => this.open(), 1000); // Try reconnecting after 1 second if .close() wasn't called
            }
        };

        this.socket.onerror = (error) => {
            console.log(`[error] ${error.message}`);
        };
    }

    // Close the WebSocket connection
    close() {
        this.shouldReconnect = false; // Prevent reconnection attempts
        if (this.socket) {
            this.socket.close();
        }
    }
}
