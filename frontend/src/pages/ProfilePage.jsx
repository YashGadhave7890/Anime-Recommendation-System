import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Star,
  Bookmark,
  Heart,
  Save,
  Check,
  History,
  Layers,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useToast } from '../context/ToastContext';
import { setUserPreferences, getWatchHistory } from '../api/interactions';

const ALL_GENRES = [
  'Action',
  'Adventure',
  'Comedy',
  'Drama',
  'Fantasy',
  'Horror',
  'Mystery',
  'Psychological',
  'Romance',
  'Sci-Fi',
  'Shounen',
  'Slice of Life',
  'Supernatural',
  'Thriller',
];

const ALL_TYPES = ['TV', 'Movie', 'OVA', 'ONA', 'Special'];

export default function ProfilePage() {
  const {
    userId,
    currentUser,
    switchUser,
    demoUsers,
    ratings,
    watchlist,
    preferences,
    refreshUserData,
  } = useUser();
  const { showToast } = useToast();

  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [history, setHistory] = useState([]);
  const [savingPrefs, setSavingPrefs] = useState(false);

  useEffect(() => {
    setSelectedGenres(preferences?.preferred_genres || []);
    setSelectedTypes(preferences?.preferred_types || ['TV', 'Movie']);
  }, [preferences]);

  useEffect(() => {
    getWatchHistory()
      .then(setHistory)
      .catch(() => setHistory([]));
  }, [userId]);

  const toggleGenre = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const toggleType = (type) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleSavePreferences = async () => {
    try {
      setSavingPrefs(true);
      await setUserPreferences(selectedGenres, selectedTypes);
      await refreshUserData();
      showToast('Anime taste preferences saved! Cold-start & hybrid models updated.');
    } catch (err) {
      showToast(err.message || 'Failed to save preferences', 'error');
    } finally {
      setSavingPrefs(false);
    }
  };

  // Stats calculation
  const avgRating = ratings.length
    ? (ratings.reduce((acc, curr) => acc + curr.rating, 0) / ratings.length).toFixed(1)
    : '—';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Profile Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-slate-800 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
          <img
            src={currentUser.avatar}
            alt={currentUser.displayName}
            className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover border-2 border-brand-500/50 shadow-glow-sm"
          />
          <div className="space-y-1">
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
                {currentUser.displayName}
              </h1>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                  currentUser.isColdStart
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}
              >
                {currentUser.isColdStart ? 'Cold Start Persona' : 'Trained Profile'}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 max-w-md">
              {currentUser.description}
            </p>
          </div>
        </div>

        {/* Persona Quick Switcher */}
        <div className="p-3 rounded-2xl bg-dark-850 border border-slate-700/80 space-y-2">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center">
            Switch Demo Account
          </div>
          <div className="flex gap-2">
            {demoUsers.map((u) => (
              <button
                key={u.id}
                onClick={() => switchUser(u.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  u.id === userId
                    ? 'bg-brand-600 text-white shadow-glow-sm'
                    : 'bg-dark-900 text-slate-400 hover:text-white'
                }`}
              >
                {u.id === 1 ? 'Demo User (1)' : 'New User (2)'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Statistics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-dark-900 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <Star className="w-4 h-4 text-amber-400" />
            <span>Total Ratings</span>
          </div>
          <div className="text-2xl font-extrabold text-white">{ratings.length}</div>
        </div>

        <div className="p-5 rounded-2xl bg-dark-900 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
            <span>Average Score</span>
          </div>
          <div className="text-2xl font-extrabold text-amber-400">{avgRating}</div>
        </div>

        <div className="p-5 rounded-2xl bg-dark-900 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <Bookmark className="w-4 h-4 text-brand-400" />
            <span>Watchlist Items</span>
          </div>
          <div className="text-2xl font-extrabold text-white">{watchlist.length}</div>
        </div>

        <div className="p-5 rounded-2xl bg-dark-900 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-medium">
            <History className="w-4 h-4 text-violet-400" />
            <span>Episodes Logged</span>
          </div>
          <div className="text-2xl font-extrabold text-white">{history.length}</div>
        </div>
      </div>

      {/* Genre & Format Preferences Editor */}
      <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Heart className="w-5 h-5 text-rose-400" />
              <span>Taste Profile &amp; Preferred Genres</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Directly steers cold-start recommendations and acts as a prior for user taste vectors.
            </p>
          </div>

          <button
            onClick={handleSavePreferences}
            disabled={savingPrefs}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs sm:text-sm shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
          >
            {savingPrefs ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span>Save Preferences</span>
          </button>
        </div>

        {/* Preferred Genres Chips */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Favorite Genres ({selectedGenres.length} selected)
          </label>
          <div className="flex flex-wrap gap-2">
            {ALL_GENRES.map((g) => {
              const isSelected = selectedGenres.includes(g);
              return (
                <button
                  key={g}
                  type="button"
                  onClick={() => toggleGenre(g)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                    isSelected
                      ? 'bg-brand-600 text-white border border-brand-400/50 shadow-glow-sm'
                      : 'bg-dark-850 hover:bg-dark-800 text-slate-300 border border-slate-700/80 hover:text-white'
                  }`}
                >
                  <span>{g}</span>
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Preferred Formats Chips */}
        <div className="space-y-2 pt-2 border-t border-slate-800/80">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Preferred Formats
          </label>
          <div className="flex flex-wrap gap-2">
            {ALL_TYPES.map((t) => {
              const isSelected = selectedTypes.includes(t);
              return (
                <button
                  key={t}
                  type="button"
                  onClick={() => toggleType(t)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                    isSelected
                      ? 'bg-brand-600 text-white border border-brand-400/50 shadow-glow-sm'
                      : 'bg-dark-850 hover:bg-dark-800 text-slate-300 border border-slate-700/80 hover:text-white'
                  }`}
                >
                  <span>{t}</span>
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* User Ratings History Table */}
      <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-slate-800 space-y-4">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Star className="w-5 h-5 text-amber-400 fill-amber-400" />
          <span>Your Rated Anime ({ratings.length})</span>
        </h2>

        {ratings.length === 0 ? (
          <p className="text-sm text-slate-400 py-6 text-center">
            You have not rated any anime yet. Visit any title page to rate it and train your taste profile!
          </p>
        ) : (
          <div className="space-y-3">
            {ratings.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-2xl bg-dark-850 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 font-extrabold flex items-center justify-center text-sm shrink-0">
                    {item.rating}
                  </div>
                  <div>
                    <Link
                      to={`/anime/${item.anime_id}`}
                      className="font-semibold text-white hover:text-brand-300 transition text-sm"
                    >
                      {item.anime?.name || `Anime #${item.anime_id}`}
                    </Link>
                    {item.review && (
                      <p className="text-xs text-slate-400 mt-0.5 line-clamp-1 italic">
                        &quot;{item.review}&quot;
                      </p>
                    )}
                  </div>
                </div>

                <div className="text-xs text-slate-400 sm:text-right shrink-0">
                  <span>Rated on: {new Date(item.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
