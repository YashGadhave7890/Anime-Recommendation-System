import apiClient from './client';

/**
 * Fetch popular baseline recommendations.
 * @param {Object} params Filter options: genre, type, min_year, max_year, top_n
 */
export async function getPopularRecommendations(params = {}) {
  const response = await apiClient.get('/api/recommendations/popular', { params });
  return response.data;
}

/**
 * Fetch personalized and hybrid recommendations for active user.
 * @param {Object} params Options: query_anime, type, top_n, w_content, w_user, w_pop
 */
export async function getPersonalizedRecommendations(params = {}) {
  const response = await apiClient.get('/api/recommendations/personalized', { params });
  return response.data;
}
