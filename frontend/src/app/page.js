'use client'
import AlignmentView from './AlignmentView.js';

export default function Page() {

  const constStars = [
    {
        "const": "And",
        "stars": [
            {
                "HIP": 677,
                "RA/DEC": "00 08 23.17 +29 05 27.0",
                "Vmag": "2.07",
                "Bayer": "alf",
                "Const": "And"
            },
            {
                "HIP": 5447,
                "RA/DEC": "01 09 43.80 +35 37 15.0",
                "Vmag": "2.07",
                "Bayer": "bet",
                "Const": "And"
            },
            {
                "HIP": 9640,
                "RA/DEC": "02 03 53.92 +42 19 47.5",
                "Vmag": "2.10",
                "Bayer": "gam01",
                "Const": "And"
            },
            {
                "HIP": 3092,
                "RA/DEC": "00 39 19.60 +30 51 40.4",
                "Vmag": "3.27",
                "Bayer": "del",
                "Const": "And"
            },
            {
                "HIP": 4436,
                "RA/DEC": "00 56 45.10 +38 29 57.3",
                "Vmag": "3.86",
                "Bayer": "mu.",
                "Const": "And"
            },
            {
                "HIP": 3881,
                "RA/DEC": "00 49 48.83 +41 04 44.2",
                "Vmag": "4.53",
                "Bayer": "nu.",
                "Const": "And"
            }
        ]
    },
    {
        "const": "Ant",
        "stars": [
            {
                "HIP": 51172,
                "RA/DEC": "10 27 09.16 -31 04 04.1",
                "Vmag": "4.28",
                "Bayer": "alf",
                "Const": "Ant"
            },
            {
                "HIP": 48926,
                "RA/DEC": "09 58 52.34 -35 53 27.4",
                "Vmag": "5.23",
                "Bayer": "eta",
                "Const": "Ant"
            }
        ]
    }]
  return <div>
    <AlignmentView constStars={constStars}/>
    </div>
}