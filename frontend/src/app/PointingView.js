'use client'
import { appContext } from './appContext.js';
import { useState, useEffect } from 'react';

export default function PointingView({isVisible}) {
    const [telescope_az, set_telescope_az] = useState(undefined);
    const [telescope_alt, set_telescope_alt] = useState(undefined);
    const [telescope_ra, set_telescope_ra] = useState(undefined);
    const [telescope_dec, set_telescope_dec] = useState(undefined);

    function updateTelescopeCoords(tc) {
        set_telescope_az(tc.alt_az_coords.az);
        set_telescope_alt(tc.alt_az_coords.alt);
        set_telescope_ra(tc.eq_coords.ra);
        set_telescope_dec(tc.eq_coords.dec);
    }

    useEffect(() => {
        appContext.websocketMessaging.register("TelescopeCoords",
            updateTelescopeCoords);
    }, [])

    return (
    <div className="mainview" is_visible={isVisible.toString()}>
        <div className="coordsbox">
            <span className="coordsobj">Telescope</span>
            <div className="coords">
                <span className="coordname">Az</span>
                {telescope_az && telescope_az.toFixed(2)}
                <span className="coordname">Alt</span> 
                {telescope_alt && telescope_alt.toFixed(2)}
            </div>
            <div className="coords">
                <span className="coordname">RA</span> 
                {telescope_ra && telescope_ra.toFixed(2)}
                <span className="coordname">Dec</span>
                {telescope_dec && telescope_dec.toFixed(2)}
            </div>
        </div>
    </div>
    );
}