'use client'

export default function TabView({onClick, tabs}) {
    function onClickWrapper(e) {
        e.stopPropagation();
        onClick(e.target.attributes._value.value)
    }
    const tab_components = tabs.map(t => {
      let classnames = "tabbutton" + (t.active ? " active" : "");
      return <button className={classnames} key={t.key} _value={t.key} disabled={t.disabled} onClick={onClickWrapper}>
        {t.text}
      </button>
    });
    
    return <div className="tabview">{tab_components}</div>;
}