'use client'

export default function SearchResult({object}) {
    const vmag = object.vmag != "99.9" && object.vmag != "79.9" ? object.vmag : "-";
    const srbr = object.sr_br != "99.9" && object.sr_br != "79.9" ? object.sr_br : "-";
    const vmag_srbr = vmag + " / " + srbr;

    return <li className="searchresult">
        <div className="searchresultline">
            <div className="objectid">{object.object_id} </div>
            <div className="con">{object.con}</div>
        </div>
        <div className="searchresultline">
            <div className="type">{object.type} </div>
            <div className="vmagsrbr">{vmag_srbr}</div>
        </div>
    </li>
}