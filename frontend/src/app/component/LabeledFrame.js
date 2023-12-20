'use client'

export default function LabeledFrame({label, children}) {
    return (
        <div className="coordsbox">
            <div className="framelabel">
                <span className="framelabel">{label || ""}</span>
            </div>
            {children}
        </div>
    );
}