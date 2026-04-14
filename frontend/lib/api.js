import axios from 'axios';

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export const fetchBooks = (params = {}) => API.get('/books/', { params });
export const fetchBookDetail = (id) => API.get(`/books/${id}/`);
export const fetchRecommendations = (id) => API.get(`/books/${id}/recommend/`);
export const fetchGenres = () => API.get('/books/genres/');
export const fetchQAHistory = () => API.get('/books/qa-history/');
export const askQuestion = (question, book_id = null) =>
  API.post('/books/ask/', { question, book_id });
export const triggerScrape = (num_pages = 5) =>
  API.post('/books/scrape/', { num_pages });
