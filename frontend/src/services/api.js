import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api' })
api.interceptors.request.use((config) => {
	const token = localStorage.getItem('access_token')
	if (token) config.headers.Authorization = `Bearer ${token}`
	return config
})
api.interceptors.response.use((response) => response, (error) => {
	if (error.response?.status === 401 && !window.location.pathname.startsWith('/signin')) {
		localStorage.removeItem('access_token')
		localStorage.removeItem('user')
		window.location.href = '/signin'
	}
	return Promise.reject(error)
})
export const getProducts = (params) => api.get('/products', { params })
export const createProduct = (data) => api.post('/products', data)
export const deleteProduct = (id) => api.delete(`/products/${id}`)
export const getStats = () => api.get('/dashboard/stats')
export const getAlerts = () => api.get('/dashboard/alerts')
export const getRecent = () => api.get('/dashboard/recent')
export const getTransactions = (params) => api.get('/transactions', { params })
export const postTransaction = (type, data) => api.post(`/transactions/${type}`, data)
export const parseCommand = (data) => api.post('/nlp/parse', data)
export const askAssistant = (data) => api.post('/assistant/query', data)
export default api
