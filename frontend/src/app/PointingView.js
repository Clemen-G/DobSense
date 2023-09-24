'use client'
import ObjectCoordsView from './ObjectCoordsView.js';
import { appContext } from './appContext.js';
import { useState, useEffect } from 'react';

export default function PointingView({isVisible}) {
    const [telescopeCoords, setTelescopeCoords] = useState(null);
    const [targetCoords, setTargetCoords] = useState(null);


    useEffect(() => {
        appContext.websocketMessaging.register("TelescopeCoords",
            tc => setTelescopeCoords(tc));
        appContext.websocketMessaging.register("TargetCoords",
            tc => setTargetCoords(tc));
    }, [])

    return (
    <div className="mainview" is_visible={isVisible.toString()}>
        <ObjectCoordsView objectName="Telescope" objectCoords={telescopeCoords}/>
        <ObjectCoordsView objectName="Target" objectCoords={targetCoords}/>
    </div>
    );
}