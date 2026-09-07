import React, { useState, useEffect } from 'react';
import { Bookmark, Trash2, CheckCircle2, Eye, Clock, XCircle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getUserWatchlist, removeFromWatchlist, addToWatchlist } from '../api/interactions';
import AnimeCard from '../components/common/AnimeCard';
import { AnimeGridSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { useUser } from '../context/UserContext';
import { useToast } from '../context/ToastContext';

const TABS = [
  { id: 'all', label: 'All Items' },
  { id: 'watching', label: 'Watching' },
  { id: 'plan_to_watch', label: 'Plan to Watch' },
  { id: 'completed', label: 'Completed' },
  { id: 'dropped', label: 'Dropped' },
];

export default function WatchlistPage() {
  const { userId, refreshUserData } = useUser();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('all');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      setError(null);
      const statusParam = activeTab === 'all' ? null : activeTab;
      const data = await getUserWatchlist(statusParam);
      setItems(data || []);
    } catch (err) {
      console.error('Watchlist fetch error:', err);
      setError(err.message || 'Failed to fetch watchlist items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, [userId, activeTab]);

  const handleRemove = async (animeId, animeTitle) => {
    try {
      await removeFromWatchlist(animeId);
      await refreshUserData();
      setItems((prev) => prev.filter((item) => item.anime_id !== animeId));
      showToast(`Removed "${animeTitle || 'Anime'}" from watchlist`);
    } catch (err) {
      showToast(err.message || 'Failed to remove from watchlist', 'error');
    }
  };

  const handleStatusChange = async (animeId, newStatus) => {
    try {
      await addToWatchlist(animeId, newStatus);
      await refreshUserData();
      fetchWatchlist();
      showToast('Status updated successfully');
    } catch (err) {
      showToast(err.message || 'Failed to update status', 'error');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-brand-400 text-xs font-bold uppercase tracking-wider">
          <Bookmark className="w-4 h-4" />
          <span>Library Management</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Your Watchlist
        </h1>
        <p className="text-slate-400 text-sm max-w-xl">
          Track titles you plan to watch, are currently enjoying, or have completed.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition ${
              activeTab === tab.id
                ? 'bg-brand-600 text-white shadow-glow-sm'
                : 'bg-dark-900 text-slate-400 hover:text-white hover:bg-dark-850'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <AnimeGridSkeleton count={8} />
      ) : error ? (
        <ErrorState
          title="Could Not Load Watchlist"
          message={error}
          onRetry={fetchWatchlist}
        />
      ) : items.length === 0 ? (
        <EmptyState
          title="Your Watchlist is Empty"
          description={
            activeTab === 'all'
              ? 'You have not added any anime to your watchlist yet. Browse the catalog to start bookmarking!'
              : `No anime found with status "${activeTab.replace('_', ' ')}".`
          }
          actionLabel="Discover Anime"
          actionTo="/discover"
          icon={Bookmark}
        />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
          {items.map((item) => {
            const anime = item.anime || { mal_id: item.anime_id, name: `Anime #${item.anime_id}` };
            return (
              <div key={item.id} className="relative group">
                <AnimeCard anime={anime} />

                {/* Status Switcher Overlay */}
                <div className="mt-2 flex items-center justify-between text-xs px-1">
                  <select
                    value={item.status}
                    onChange={(e) => handleStatusChange(item.anime_id, e.target.value)}
                    className="bg-dark-850 border border-slate-700 text-slate-300 text-[11px] font-medium rounded-lg px-2 py-1 focus:outline-none focus:border-brand-500"
                  >
                    <option value="plan_to_watch">Plan to Watch</option>
                    <option value="watching">Watching</option>
                    <option value="completed">Completed</option>
                    <option value="dropped">Dropped</option>
                  </select>

                  <button
                    onClick={() => handleRemove(item.anime_id, anime.name)}
                    className="p-1 rounded-md text-slate-500 hover:text-rose-400 transition"
                    title="Remove from watchlist"
                    aria-label="Remove"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
