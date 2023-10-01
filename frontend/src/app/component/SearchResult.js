'use client'

export default function SearchResult({object, selected, onClickHandler}) {
    const vmag = object.vmag != "99.9" && object.vmag != "79.9" ? object.vmag : "-";
    const srbr = object.sr_br != "99.9" && object.sr_br != "79.9" ? object.sr_br : "-";
    const vmag_srbr = vmag + " / " + srbr;

    const obj_name = object.object_id + (object.m_short ? " (" + object.m_short + ")" : "");

    return <li className="searchresult"
            object_id={object.object_id}
            selected={selected ? "" : false}
            onClick={onClickHandler}>
        <div className="searchresultline">
            <div className="objectname">{obj_name}</div>
            <div className="con">{object.con}</div>
        </div>
        <div className="searchresultline">
            <div className="type">{object.type} </div>
            <div className="vmagsrbr">{vmag_srbr}</div>
        </div>
    </li>
}