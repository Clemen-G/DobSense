'use client'

import { appContext } from "./appContext";

export default class WebsocketMessaging {
    static IS_ALIGNED_MESSAGE = "IsAlignedMessage";
    static ALIGNMENT_POINTS_MESSAGE = "AlignmentPointsMessage";
    static TELESCOPE_COORDS_MESSAGE = "TelescopeCoordsMessage";
    static TARGET_COORDS_MESSAGE = "TargetCoordsMessage";

    constructor() {
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
    async open(url) {
        console.log('WebsocketMessaging.open()');
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        const doOpen = (location) => {
            this.shouldReconnect = true;
            this.socket = new WebSocket(url);
            this.socket.onmessage = this.handleMessage.bind(this);
            console.log("opening websocket")

            this.socket.onopen = () => {
                console.log('WebSocket opened, sending HelloMessage');
                const helloMessage = {
                    location: location,
                    timestamp: new Date().getTime() / 1000.0,
                    "messageType": "HelloMessage"
                }
                this.socket.send(JSON.stringify(helloMessage))
            };

            this.socket.onclose = (event) => {
                if (event.wasClean) {
                    console.log('Closed cleanly');
                } else {
                    console.log('Connection died');
                }

                if (this.shouldReconnect) {
                    console.log("Reconnecting...");
                    setTimeout(() => this.open(url), 2000); // Try reconnecting after xx second if .close() wasn't called
                }
            };

            this.socket.onerror = (error) => {
                console.log(`websocketMessaging [error] ${error}`);
            };
        }

        console.log("WebsocketMessaging: getting location");
        return appContext.getLocation()
            .then(doOpen);
    }

    // Close the WebSocket connection
    close() {
        console.log('WebsocketMessaging.close()');
        this.shouldReconnect = false; // Prevent reconnection attempts
        if (this.socket) {
            this.socket.close();
        }
    }
}
