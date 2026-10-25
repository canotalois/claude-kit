import { readFile } from 'node:fs/promises'
import { loadConfig } from './config.ts'

const config = loadConfig(process.env)
const pkg: unknown = JSON.parse(await readFile('package.json', 'utf8'))
console.log(config.apiUrl, typeof pkg)
