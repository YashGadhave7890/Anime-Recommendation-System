import apiClient from './client';

// -----------------------------------------------------------------------------
// Ratings
// -----------------------------------------------------------------------------

export async function getUserRatings() {
  const response = await apiClient.get('/api/ratings');
  return response.data;
}

export async function submitRating(animeId, rating, review = null) {
  const response = await apiClient.post('/api/ratings', {
    anime_id: Number(animeId),
    rating: Number(rating),
    review: review || null,
  });
  return response.data;
}

// -----------------------------------------------------------------------------
// Watchlist
// -----------------------------------------------------------------------------

export async function getUserWatchlist(status = null) {
  const params = status ? { status } : {};
  const response = await apiClient.get('/api/watchlist', { params });
  return response.data;
}

export async function addToWatchlist(animeId, status = 'plan_to_watch') {
  const response = await apiClient.post('/api/watchlist', {
    anime_id: Number(animeId),
    status,
  });
  return response.data;
}

export async function removeFromWatchlist(animeId) {
  const response = await apiClient.delete(`/api/watchlist/${animeId}`);
  return response.data;
}

// -----------------------------------------------------------------------------
// Watch History
// -----------------------------------------------------------------------------

export async function getWatchHistory() {
  const response = await apiClient.get('/api/history');
  return response.data;
}

export async function logWatchProgress(animeId, progressEpisodes = 1) {
  const response = await apiClient.post('/api/history', {
    anime_id: Number(animeId),
    progress_episodes: Number(progressEpisodes),
  });
  return response.data;
}

// -----------------------------------------------------------------------------
// User Preferences
// -----------------------------------------------------------------------------

export async function getUserPreferences() {
  const response = await apiClient.get('/api/preferences');
  return response.data;
}

export async function setUserPreferences(preferredGenres = [], preferredTypes = []) {
  const response = await apiClient.post('/api/preferences', {
    preferred_genres: preferredGenres,
    preferred_types: preferredTypes,
  });
  return response.data;
}
