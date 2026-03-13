import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const movieAPI = {
  getTrending: (limit = 20) => api.get(`/movies/trending?limit=${limit}`),
  getRecommendations: (userId, mood = null, model = 'hybrid', limit = 20) =>
    api.get(`/movies/recommendations?user_id=${userId}&model=${model}&limit=${limit}${mood ? `&mood=${mood}` : ''}`),
  search: (q, mode = 'semantic', limit = 20) =>
    api.get(`/movies/search?q=${encodeURIComponent(q)}&mode=${mode}&limit=${limit}`),
  getSimilar: (movieId, limit = 10) => api.get(`/movies/${movieId}/similar?limit=${limit}`),
  rateMovie: (userId, movieId, rating) =>
    api.post('/movies/rate', { user_id: userId, movie_id: movieId, rating }),
  getMoodRecs: (mood, limit = 20) => api.get(`/movies/mood/${mood}?limit=${limit}`),
  getMovieById: (movieId) => api.get(`/movies/${movieId}`),
};

export const userAPI = {
  getHistory: (userId) => api.get(`/users/${userId}/history`),
  getRatings: (userId) => api.get(`/users/${userId}/ratings`),
  addToHistory: (userId, movieId, title) =>
    api.post(`/users/${userId}/history?movie_id=${movieId}&title=${encodeURIComponent(title)}`),
  getTasteProfile: (userId) => api.get(`/users/${userId}/taste-profile`),
};

export default api;
