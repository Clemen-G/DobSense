'use client'

import axios from 'axios';

import { useState } from 'react';
import { appContext } from './appContext.js';


export default function AlignmentView({constellationsStars, isVisible}) {
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
          console.log("alignment completed");
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
        })
        .finally(function () {
          // always executed
        }); 
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

    return <div className="mainview" is_visible={isVisible.toString()}>
        <select onChange={constSelectedHandler}>{constsOptions}</select>
        {starSelector}
        <button disabled={selectedStar === ""} onClick={submitAlignment}>
            Confirm centered
        </button>
        <button disabled={alignments.length < 3} onClick={requestAlignment}>
            Align telescope
        </button>
      </div>
  }