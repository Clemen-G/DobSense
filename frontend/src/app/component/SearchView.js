'use client'
import axios from 'axios';
import Fuse from 'fuse.js';
import { appContext } from '../appContext.js';
import { useState, useEffect, useRef } from 'react';
import SearchResult from './SearchResult.js'

export default function SearchView({onTargetSet, isVisible}) {
    const fuse = useRef(null);
    const [searchString, setSearchString] = useState('');
    const [candidateTarget, setCandidateTarget] = useState(null);

    function loadObjects() {
        axios.get('/api/objects')
        .then(function (response) {
            initFuse(response.data)
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
        })
        .finally(function () {
          // always executed
        }); 
    };

    function setTarget(e) {
        const payload = {object_id: candidateTarget}
        axios.put('/api/target', payload)
        .then(function (response) {
          console.log("target set");
        })
        .then(function () {
            if (onTargetSet) {
                onTargetSet();
            }
        })
        .catch(function (error) {
          appContext.apiErrorHandler(error);
        })
        .finally(function () {
          // always executed
        }); 
    }

    function initFuse(catalog) {
        const fuseOptions = {
            // isCaseSensitive: false,
            // includeScore: false,
            // shouldSort: true,
            // includeMatches: false,
            // findAllMatches: false,
            // minMatchCharLength: 1,
            // location: 0,
            threshold: 0.0,
            // distance: 100,
            useExtendedSearch: true,
            ignoreLocation: true,
            // ignoreFieldNorm: false,
            // fieldNormWeight: 1,
            keys: [
                "flattened"
            ]
        };
        console.log('initing fuse');
        const attrs = [
            "object_id",
            "other_names",
            "type",
            "con",
            "m_long",
            "m_short"
        ];
        // fuse does not support "spreading" the search across different fields,
        // so I'm concating all fields of interest in a single one.
        function add_flattened(entry) {
            const flattened_tokens = attrs.map(a => entry[a]).join(" ");
            entry["flattened"] = flattened_tokens;
        }
        
        catalog.forEach(add_flattened);

        fuse.current = new Fuse(catalog, fuseOptions);
        console.log('SearchView: completed fuse initialization');
    }

    useEffect(loadObjects, []);

    let searchResults =[]
    if (fuse.current) {
        searchResults = fuse.current.search(searchString, {limit: 50})
            .map(r => <SearchResult
                        object={r.item}
                        key={r.item.object_id}
                        selected={r.item.object_id === candidateTarget}
                        onClickHandler={e => setCandidateTarget(e.currentTarget.attributes.object_id.value)}/>);
    }

    return (
        <div className="mainview" is_visible={isVisible.toString()}>
            <div className="searchinput">
                <input
                    value={searchString}
                    onChange={e => setSearchString(e.target.value)}
                />
            </div>
            <ul className='searchresults'>
                {searchResults}
            </ul>
            <button disabled={candidateTarget === null} onClick={setTarget}>
                Target {candidateTarget}
            </button>
        </div>
    );
}