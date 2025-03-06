'use client'

export default function LabeledFrame({label, children, classes}) {
    let className="labeledframe" + (classes ? " " + classes : "");
    return (
        <div className={className}>
            <div className="framelabel">
                <span className="framelabel">{label || ""}</span>
            </div>
            {children}
        </div>
    );
}