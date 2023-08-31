'use client'
import Button from './button.js'
import TextView from './textview.js'
import { useState } from 'react';

export default function Page() {
  const [count, setCount] = useState(0);
  function clickHandler() {
    setCount(count + 1);
  }
  return <div>
    <Button value="click here" clickHandler={clickHandler}/>
    <TextView text={count}></TextView>
    </div>
}