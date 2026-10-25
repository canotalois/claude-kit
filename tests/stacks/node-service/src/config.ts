export type Config = { readonly apiUrl: string }

export function loadConfig(env: NodeJS.ProcessEnv): Config {
  const apiUrl = env['API_URL']
  if (apiUrl === undefined || apiUrl === '') {
    throw new Error('Missing required environment variable API_URL')
  }
  return { apiUrl }
}
