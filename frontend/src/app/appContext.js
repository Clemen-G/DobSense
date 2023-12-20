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
    getLocation: async function() {
        console.log("getLocation()");
        return new Promise((resolve, reject) => {
            const onPosition = (pos) => {
              const coords = pos.coords;
              const location = {
                accuracy: coords.accuracy,
                altitude: coords.altitude,
                altitudeAccuracy: coords.altitudeAccuracy,
                latitude: coords.latitude,
                longitude: coords.longitude
              }
              console.log("getLocation(): location received");
              resolve(location);
            }
            navigator.geolocation.getCurrentPosition(onPosition, reject);
        });
    },
    websocketMessaging: new WebsocketMessaging()
}
