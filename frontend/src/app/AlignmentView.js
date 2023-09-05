'use client'
import { useState } from 'react';

export default function AlignmentView({constStars}) {
    const [selectedConst, setSelectedConst] = useState("");
    const [selectedStar, setSelectedStar] = useState("");

    function constSelectedHandler(e) {
        e.stopPropagation();
        setSelectedConst(e.target.value);
        setSelectedStar("");
    }
    function starSelectedHandler(e) {
        e.stopPropagation();
        setSelectedStar(e.target.value);
    }

    const constsOptions = [<option key="" value="">Pick a constellation</option>].concat(
        constStars
        .map((e) => e.const)
        .map( (constName) => <option key={constName} value={constName}>{constName}</option>));
    
    let starOptions = ""
    if (selectedConst != "") {
        starOptions = [<option key="" value="">Pick a star</option>].concat(
            constStars.filter( e => e.const == selectedConst)
                .map(e => e.stars)
                .flat()
                .map(s =>
                    <option key={s["HIP"]} value={s["HIP"]}>
                        {s["Bayer"] + " - " + s["Vmag"]}
                    </option>));
    }
    const starSelector = 
        <select key={selectedConst} onChange={starSelectedHandler} disabled={selectedConst == ""}>
            {starOptions}
        </select>

    console.log(selectedConst + " " + selectedStar);

    return <div>
        <div>
            <select onChange={constSelectedHandler}>{constsOptions}</select>
        </div>
        <div>
            {starSelector}
        </div>
        <button disabled={selectedStar == ""}>Confirm centered</button>
        <button disabled={selectedStar == ""}>Align telescope</button>
      </div>
  }