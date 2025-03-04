'use client'

export default function LabeledFrame({label, children}) {
    return (
        <div className="labeledframe">
            <div className="framelabel">
                <span className="framelabel">{label || ""}</span>
            </div>
            {children}
        </div>
    );
}