'use client'

import WebsocketMessaging  from './WebsocketMessaging.js'

export const appContext = {
    // global API error handler
    apiErrorHandler: function(e) {
        if (e.code === "ERR_BAD_REQUEST" && e.response.data.error_message) {
          this.setErrorMessage(e.response.data.error_message);
        }
        else {
          this.setErrorMessage(e.code);
          console.log(e);
        }
    },
    websocketMessaging: new WebsocketMessaging('wss://' + window.location.host + '/api/websocket')
}
