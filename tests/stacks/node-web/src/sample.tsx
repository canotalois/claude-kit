import Link from 'next/link'
import { useState } from 'react'

type Status = { status: 'loading' } | { status: 'ready'; items: readonly string[] }

export function describe(state: Status): string {
  switch (state.status) {
    case 'loading':
      return 'Loading'
    case 'ready':
      return `${String(state.items.length)} items`
  }
}

export function grouped(orders: readonly { region: string }[]) {
  return Object.groupBy(orders, (o) => o.region)
}

export class AuthError extends Error {
  readonly code: 'INVALID_CREDENTIALS' | 'ACCOUNT_LOCKED'

  constructor(code: AuthError['code'], message: string, options?: ErrorOptions) {
    super(message, options)
    this.name = 'AuthError'
    this.code = code
  }
}

export function Counter() {
  const [count, setCount] = useState(0)
  return (
    <div>
      <button type="button" aria-label="Increment" onClick={() => { setCount(count + 1) }}>+</button>
      <Link href="/settings">Settings</Link>
    </div>
  )
}
