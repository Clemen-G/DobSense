'use client'
import { useState } from 'react';

export default function AlignmentView({constellationsStars}) {
    const [selectedConst, setSelectedConst] = useState("");
    const [selectedStar, setSelectedStar] = useState("");
    const [alignments, setAlignments] = useState([]);

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
        constellationsStars
        .map((e) => e.const)
        .map( (constName) => <option key={constName} value={constName}>{constName}</option>));
    
    let starOptions = ""
    if (selectedConst != "") {
        starOptions = [<option key="" value="">Pick a star</option>].concat(
            constellationsStars.filter( e => e.const == selectedConst)
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

    function submitAlignment(e) {
        const payload = {
          hip: selectedStar,
          timestamp: new Date().getTime()
        }
        axios.put('/api/alignments', payload)
        .then(function (response) {
          setAlignments(response.data.alignment_points)
        })
        .catch(function (error) {
          console.log(error);
        })
        .finally(function () {
          // always executed
        }); 
      }
    
    return <div>
        <div>
            <select onChange={constSelectedHandler}>{constsOptions}</select>
        </div>
        <div>
            {starSelector}
        </div>
        <button disabled={selectedStar == ""} onClick={submitAlignment}>
            Confirm centered
        </button>
        <button disabled={alignments.length < 3}>Align telescope</button>
      </div>
  }