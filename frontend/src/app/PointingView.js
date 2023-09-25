'use client'
import ObjectCoordsView from './ObjectCoordsView.js';
import PointingAid from './component/PointingAid.js';
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