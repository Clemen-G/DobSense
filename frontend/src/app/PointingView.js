'use client'
import { appContext } from './appContext.js';
import { useState, useEffect } from 'react';

export default function PointingView({isVisible}) {
    const [telescope_az, set_telescope_az] = useState(undefined);
    const [telescope_alt, set_telescope_alt] = useState(undefined);

    function updateTelescopeCoords(tc) {
        set_telescope_az(tc.alt_az_coords.az);
        set_telescope_alt(tc.alt_az_coords.alt);
    }

    useEffect(() => {
        appContext.websocketMessaging.register("TelescopeCoords",
            updateTelescopeCoords);
    }, [])

    return <div is_visible={isVisible.toString()}>
        {telescope_az && telescope_az.toFixed(2)} {telescope_az && telescope_alt.toFixed(2)}</div>
}