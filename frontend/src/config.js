// Central API base URL — uses env variable in production, localhost in dev
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default API
