import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [greet, setgreet] = useState("")

  async function callGreet() {
      if (window.paneer) {
        let res = await window.paneer.invoke("greet", {});
        setgreet(res);
      } else {
        setgreet("Paneer not detected");
      }
  }

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React + Paneer</h1>
      <div className="card">
        <button onClick={callGreet}>
          Greet!
        </button>
        <p className='greet'>
          {greet}
        </p>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
