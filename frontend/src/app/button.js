'use client'
export default function Button({value, clickHandler}) {
    return <button onClick={clickHandler}>
    {value}
  </button>
}