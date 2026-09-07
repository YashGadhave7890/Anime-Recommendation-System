import apiClient from './client';

/**
 * Fetch paginated and filtered anime catalog.
 * @param {Object} params Query parameters: page, limit, genre, type, min_score, min_year, max_year, sort_by, order
 */
export async function getAnimeList(params = {}) {
  const response = await apiClient.get('/api/anime', { params });
  return response.data;
}

/**
 * Fetch full anime detail by MyAnimeList ID.
 * @param {number|string} malId
 */
export async function getAnimeDetail(malId) {
  const response = await apiClient.get(`/api/anime/${malId}`);
  return response.data;
}

/**
 * Search anime titles using prefix, substring, or fuzzy matching.
 * @param {string} query
 * @param {number} limit
 */
export async function searchAnime(query, limit = 10) {
  if (!query || !query.trim()) return [];
  const response = await apiClient.get('/api/anime/search', {
    params: { q: query.trim(), limit },
  });
  return response.data;
}

/**
 * Fetch content-based similar anime using TF-IDF cosine similarity.
 * @param {number|string} malId
 * @param {number} topN
 */
export async function getSimilarAnime(malId, topN = 10) {
  const response = await apiClient.get(`/api/anime/${malId}/similar`, {
    params: { top_n: topN },
  });
  return response.data;
}
