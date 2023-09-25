'use client'
import React, { useRef, useEffect, useState } from 'react';
import { SVG } from '@svgdotjs/svg.js';

export default function PointingAid({scope_taz, scope_talt, target_taz, target_talt}) {
    const containerRef = useRef(null);
    const [svgCanvas, setSvgCanvas] = useState(null);

    const delta_taz_360 = (target_taz - scope_taz) % 360;
    // -180 <= delta_taz <= 180 to recommend and view smallest rotation
    const delta_taz = delta_taz_360 <= 180 ? delta_taz_360 : delta_taz_360 - 360
    const delta_talt = target_talt - scope_talt;

    const canvas_x = 300;
    const canvas_y = canvas_x / 2;
    const is_zoom = Math.abs(delta_taz) < 10 && Math.abs(delta_talt) < 5;
    const view_taz =  is_zoom ? 12 : 180;
    const view_talt = is_zoom ? 6 : 90;
    const search_circle_radius = is_zoom ? 1 : 5;

    useEffect(() => {
        if (containerRef.current) {
            // Create the SVG canvas if it does not exist
            let draw = null;
            if (! svgCanvas) {
                draw = SVG().addTo(containerRef.current).size(canvas_x, canvas_y);
                setSvgCanvas(draw);
            }
            else {
                draw = svgCanvas;
            }

            draw.clear();

            draw.text("\u0394taz:  "+delta_taz.toFixed(1))
                .font({family:   'monospace', size: 14})
                .move(0,16).stroke("red").fill("red");
            draw.text("\u0394talt: "+delta_talt.toFixed(1))
                .font({family:   'monospace', size: 14})
                .move(0,32).stroke("red").fill("red");

            draw.circle(search_circle_radius / view_taz * (canvas_x/2))
                .fill("none").stroke("red")
                .center(canvas_x/2, canvas_y/2);
            
            draw.circle(5).fill('#39f')
                .center(
                    canvas_x/2 + delta_taz / view_taz * (canvas_x/2),
                    canvas_y/2 - delta_talt / view_talt * (canvas_y/2) // y coord is inverted in svg canvas
                );
        }
    }, [scope_taz, scope_talt, target_taz, target_talt]);

    return <div className="pointingaid" ref={containerRef}/>
};