'use client'

import LabeledFrame from "./LabeledFrame";

export default function ObjectCoordsView({objectName, objectCoords}) {
   let coords_widgets = [
    {
        label_1: "Az",
        label_2: "Alt",
        coord_1: objectCoords && objectCoords.alt_az_coords.az.toFixed(2),
        coord_2: objectCoords && objectCoords.alt_az_coords.alt.toFixed(2)
    },
    {
        label_1: "RA",
        label_2: "Dec",
        coord_1: objectCoords && objectCoords.eq_coords.ra.toFixed(2),
        coord_2: objectCoords && objectCoords.eq_coords.dec.toFixed(2)
    }
   ].map(w => <div className="coords" key={w.label_1}>
    <div className="coord">
        <div className="coordname">{w.label_1}</div>
        <div className="coordvalue">{w.coord_1}</div>
    </div>
    <div className="coord">
        <div className="coordname">{w.label_2}</div> 
        <div className="coordvalue">{w.coord_2}</div>
    </div>
</div>)

    return (
        <LabeledFrame label={objectName}>
            <div className="coordsbox">
                {coords_widgets}
            </div>
        </LabeledFrame>
    );
}