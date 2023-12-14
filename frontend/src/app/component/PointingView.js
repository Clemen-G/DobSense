'use client'
import ObjectCoordsView from './ObjectCoordsView.js';
import PointingAid from './PointingAid.js';
import { appContext } from '../appContext.js';
import { useState, useEffect } from 'react';
import WebsocketMessaging from '../WebsocketMessaging.js';

export default function PointingView({isVisible}) {
    const [telescopeCoords, setTelescopeCoords] = useState(null);
    const [targetCoords, setTargetCoords] = useState(null);


    useEffect(() => {
        appContext.websocketMessaging.register(
            WebsocketMessaging.TELESCOPE_COORDS_MESSAGE,
            tc => setTelescopeCoords(tc.telescope_coords));
        appContext.websocketMessaging.register(
            WebsocketMessaging.TARGET_COORDS_MESSAGE,
            tc => setTargetCoords(tc.target_coords));
    }, [])

    const pointingAid = targetCoords ?
        <PointingAid scope_taz={telescopeCoords.taz_coords.taz} 
            scope_talt={telescopeCoords.taz_coords.talt}
            target_taz={targetCoords.taz_coords.taz}
            target_talt={targetCoords.taz_coords.talt}/> :
        ""

    return (
    <div className="mainview" is_visible={isVisible.toString()}>
        <ObjectCoordsView objectName="Telescope" objectCoords={telescopeCoords}/>
        <ObjectCoordsView objectName={targetCoords && targetCoords.object_id} objectCoords={targetCoords}/>
        {pointingAid}
    </div>
    );
}