'use client'
import { useState, useContext } from 'react';
import { AppContext } from './appContext.js';


export default function AlignmentView({constellationsStars}) {
    const [selectedConst, setSelectedConst] = useState("");
    const [selectedStar, setSelectedStar] = useState("");
    const [alignments, setAlignments] = useState([]);
    const appContext = useContext(AppContext);

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
          object_id: parseInt(selectedStar),
          timestamp: new Date().getTime() / 1000.0
        }
        axios.put('/api/alignments', payload)
        .then(function (response) {
          setAlignments(response.data.alignment_points)
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
        })
        .finally(function () {
          // always executed
        }); 
    }

    function requestAlignment(e) {
        axios.get('/api/alignment')
        .then(function (response) {
            console.log("alignment requested");
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
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
        <button disabled={alignments.length < 3} onClick={requestAlignment}>
            Align telescope
        </button>
      </div>
  }