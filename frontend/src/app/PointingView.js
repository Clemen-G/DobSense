'use client'
import ObjectCoordsView from './ObjectCoordsView.js';
import { appContext } from './appContext.js';
import { useState, useEffect } from 'react';

export default function PointingView({isVisible}) {
    const [telescopeCoords, setTelescopeCoords] = useState(null);

    function updateTelescopeCoords(tc) {
        setTelescopeCoords(tc);
    }

    useEffect(() => {
        appContext.websocketMessaging.register("TelescopeCoords",
            updateTelescopeCoords);
    }, [])

    return (
    <div className="mainview" is_visible={isVisible.toString()}>
        <ObjectCoordsView objectName="Telescope" objectCoords={telescopeCoords}/>
    </div>
    );
}