import { useState } from 'preact/hooks'

export function App() {
  const [count, setCount] = useState(0)

  return (
    <div class="counter-container">
      <h1>Hello World</h1>
      <p>Vite + Preact Counter Demo</p>
      <div class="counter">
        <button onClick={() => setCount((c) => c - 1)}>-</button>
        <span class="count">{count}</span>
        <button onClick={() => setCount((c) => c + 1)}>+</button>
      </div>
    </div>
  )
}
