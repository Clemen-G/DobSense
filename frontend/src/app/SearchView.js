'use client'
import axios from 'axios';
import Fuse from 'fuse.js';
import { appContext } from './appContext.js';
import { useState, useEffect, useRef } from 'react';
import SearchResult from './SearchResult.js'

export default function SearchView({isVisible}) {
    const fuse = useRef(null);
    const [searchString, setSearchString] = useState('');

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

    function initFuse(catalog) {
        const fuseOptions = {
            // isCaseSensitive: false,
            // includeScore: false,
            // shouldSort: true,
            // includeMatches: false,
            // findAllMatches: false,
            // minMatchCharLength: 1,
            // location: 0,
            // threshold: 0.6,
            // distance: 100,
            // useExtendedSearch: false,
            // ignoreLocation: false,
            // ignoreFieldNorm: false,
            // fieldNormWeight: 1,
            keys: [
                "object_id",
                "other_names",
                "type",
                "con"
            ]
        };
        console.log('initing fuse');
        fuse.current = new Fuse(catalog, fuseOptions);
        console.log('completed fuse initialization');
    }

    useEffect(loadObjects, []);

    let searchResults =[]
    if (fuse.current) {
        searchResults = fuse.current.search(searchString, {limit: 20})
            .map(r => <SearchResult object={r.item}/>);
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
        </div>
    );
}