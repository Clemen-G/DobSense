'use client'
import React, { useRef, useEffect, useState } from 'react';
import { SVG } from '@svgdotjs/svg.js';
import LabeledFrame from './LabeledFrame';

export default function PointingAid({scope_taz, scope_talt, target_taz, target_talt}) {
    const containerRef = useRef(null);
    const [svgCanvas, setSvgCanvas] = useState(null);

    const delta_taz_360 = (target_taz - scope_taz) % 360;
    // -180 <= delta_taz <= 180 to recommend and view smallest rotation
    const delta_taz = delta_taz_360 <= 180 ? delta_taz_360 : delta_taz_360 - 360
    const delta_talt = target_talt - scope_talt;

    // az spans 360, alt 180. storing the ratio to base calculations on a single value.
    const az_alt_ratio = 2;
    const canvas_x = 300;
    const canvas_y = canvas_x / az_alt_ratio;
    // view will rescale if -e.g. dtaz < 30 && talt < 15
    const rescale_thresholds = [
        2, 5, 30, 180
    ]
    // zoom views get a margin so that the point shows well inside the drawing area on zoom in.
    const margin_factor = 1.1;
    const search_circle_radius = 1;

    const active_threshold = rescale_thresholds.find(t => Math.max(Math.abs(delta_taz), Math.abs(delta_talt*2)) < t);
    const view_taz = active_threshold == 180 ? active_threshold : active_threshold * margin_factor;
    
    const view_talt = view_taz / az_alt_ratio;

    useEffect(() => {
        if (containerRef.current) {
            // Create the SVG canvas if it does not exist
            let canvas = null;
            if (! svgCanvas) {
                containerRef.current.ch
                canvas = SVG(containerRef.current).size(canvas_x, canvas_y);
                setSvgCanvas(canvas);
            }
            else {
                canvas = svgCanvas;
            }

            canvas.clear();

            let search_circle_radius_px = search_circle_radius / view_taz * (canvas_x/2)
            const search_circle_radius_fill = search_circle_radius_px < 5 ?
                "red" :
                "none";
            search_circle_radius_px = Math.max(search_circle_radius_px, 5);

            canvas.circle(search_circle_radius_px)
                .fill(search_circle_radius_fill)
                .stroke("red")
                .center(canvas_x/2, canvas_y/2);
            
            canvas.circle(5).fill('#39f')
                .center(
                    canvas_x/2 + delta_taz / view_taz * (canvas_x/2),
                    canvas_y/2 - delta_talt / view_talt * (canvas_y/2) // y coord is inverted in svg canvas
                );
        }
    }, [scope_taz, scope_talt, target_taz, target_talt]);

    const text = "\u0394taz:  " + delta_taz.toFixed(1) + "; \u0394talt: "+delta_talt.toFixed(1);
    return <LabeledFrame label={text}>
        <div className="pointingaid">
            <svg xmlns="http://www.w3.org/2000/svg" version="1.1" ref={containerRef}/>
        </div>
        </LabeledFrame>;
};