import { strict as assert } from 'node:assert'
import { test } from 'node:test'
import { loadConfig } from './config.ts'

test('loadConfig throws when API_URL is missing', () => {
  assert.throws(() => loadConfig({}), /API_URL/)
})
