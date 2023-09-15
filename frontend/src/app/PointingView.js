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
    <div is_visible={isVisible.toString()}>
        <div>{telescope_az && telescope_az.toFixed(2)} {telescope_alt && telescope_alt.toFixed(2)}</div>
        <div>{telescope_ra && telescope_ra.toFixed(3)} {telescope_dec && telescope_dec.toFixed(3)}</div>
    </div>
    );
}