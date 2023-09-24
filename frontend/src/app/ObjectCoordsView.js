'use client'

export default function ObjectCoordsView({objectName, objectCoords}) {
    return (
        <div className="coordsbox">
            <span className="coordsobj">{objectName}</span>
            <div className="coords">
                <span className="coordname">Az</span>
                {objectCoords && objectCoords.alt_az_coords.az.toFixed(2)}
                <span className="coordname">Alt</span> 
                {objectCoords && objectCoords.alt_az_coords.alt.toFixed(2)}
            </div>
            <div className="coords">
                <span className="coordname">RA</span> 
                {objectCoords && objectCoords.eq_coords.ra.toFixed(2)}
                <span className="coordname">Dec</span>
                {objectCoords && objectCoords.eq_coords.ra.toFixed(2)}
            </div>
        </div>
    );
}