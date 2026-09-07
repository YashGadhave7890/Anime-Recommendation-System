import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { getUserRatings, getUserWatchlist, getUserPreferences } from '../api/interactions';

const UserContext = createContext();

export const DEMO_USERS = [
  {
    id: 1,
    username: 'demo_user',
    displayName: 'Shinji (Experienced Otaku)',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
    description: 'Warm profile with ratings for Death Note, FMAB, Steins;Gate, and genre preferences.',
    isColdStart: false,
  },
  {
    id: 2,
    username: 'new_user',
    displayName: 'Aoi (New Explorer)',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
    description: 'Clean cold-start profile with zero ratings. Demonstrates cold-start fallback.',
    isColdStart: true,
  },
];

export function UserProvider({ children }) {
  const [userId, setUserId] = useState(() => {
    return Number(localStorage.getItem('animora_user_id')) || 1;
  });

  const [ratings, setRatings] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [preferences, setPreferences] = useState({ preferred_genres: [], preferred_types: [] });
  const [loading, setLoading] = useState(false);

  const currentUser = DEMO_USERS.find((u) => u.id === userId) || DEMO_USERS[0];

  const switchUser = useCallback((newId) => {
    const idNum = Number(newId);
    setUserId(idNum);
    localStorage.setItem('animora_user_id', String(idNum));
  }, []);

  const refreshUserData = useCallback(async () => {
    try {
      setLoading(true);
      const [ratingsData, watchlistData, prefsData] = await Promise.all([
        getUserRatings().catch(() => []),
        getUserWatchlist().catch(() => []),
        getUserPreferences().catch(() => ({ preferred_genres: [], preferred_types: [] })),
      ]);
      setRatings(ratingsData);
      setWatchlist(watchlistData);
      setPreferences(prefsData);
    } catch (err) {
      console.warn('Failed to fetch user interaction state:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUserData();
  }, [userId, refreshUserData]);

  // Fast lookup helpers
  const getWatchlistStatus = useCallback((animeId) => {
    const item = watchlist.find((w) => w.anime_id === Number(animeId));
    return item ? item.status : null;
  }, [watchlist]);

  const getUserRatingVal = useCallback((animeId) => {
    const r = ratings.find((item) => item.anime_id === Number(animeId));
    return r ? r.rating : null;
  }, [ratings]);

  const contextValue = useMemo(() => ({
    userId,
    currentUser,
    switchUser,
    ratings,
    watchlist,
    preferences,
    loading,
    refreshUserData,
    getWatchlistStatus,
    getUserRatingVal,
    demoUsers: DEMO_USERS,
  }), [userId, currentUser, switchUser, ratings, watchlist, preferences, loading, refreshUserData, getWatchlistStatus, getUserRatingVal]);

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
