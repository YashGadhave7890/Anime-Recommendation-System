import React, { useState, useRef, useEffect } from 'react';
import { Bookmark, BookmarkCheck, ChevronDown, Check, Trash2 } from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { useToast } from '../../context/ToastContext';
import { addToWatchlist, removeFromWatchlist } from '../../api/interactions';

const STATUS_CONFIG = {
  plan_to_watch: { label: 'Plan to Watch', color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30' },
  watching: { label: 'Watching', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
  completed: { label: 'Completed', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
  dropped: { label: 'Dropped', color: 'text-slate-400 bg-slate-500/10 border-slate-500/30' },
};

export default function WatchlistButton({ animeId, animeTitle, compact = false }) {
  const { getWatchlistStatus, refreshUserData } = useUser();
  const { showToast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  const currentStatus = getWatchlistStatus(animeId);
  const isBookmarked = !!currentStatus;

  // Close dropdown on outside click or Escape key
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleSetStatus = async (status, e) => {
    e.stopPropagation();
    try {
      setLoading(true);
      await addToWatchlist(animeId, status);
      await refreshUserData();
      showToast(`Updated "${animeTitle || 'Anime'}" status to ${STATUS_CONFIG[status]?.label}`);
      setIsOpen(false);
    } catch (err) {
      showToast(err.message || 'Failed to update watchlist', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (e) => {
    e.stopPropagation();
    try {
      setLoading(true);
      await removeFromWatchlist(animeId);
      await refreshUserData();
      showToast(`Removed "${animeTitle || 'Anime'}" from watchlist`, 'info');
      setIsOpen(false);
    } catch (err) {
      showToast(err.message || 'Failed to remove from watchlist', 'error');
    } finally {
      setLoading(false);
    }
  };

  const toggleDropdown = (e) => {
    e.stopPropagation();
    setIsOpen(!isOpen);
  };

  if (compact) {
    return (
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={toggleDropdown}
          disabled={loading}
          aria-haspopup="menu"
          aria-expanded={isOpen}
          className={`p-2 rounded-xl backdrop-blur-md transition-all duration-200 border focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
            isBookmarked
              ? 'bg-brand-600/90 text-white border-brand-400/50 shadow-glow-sm'
              : 'bg-dark-900/80 text-slate-300 border-white/10 hover:bg-slate-800 hover:text-white'
          }`}
          title={isBookmarked ? `In Watchlist (${STATUS_CONFIG[currentStatus]?.label})` : 'Add to Watchlist'}
          aria-label={isBookmarked ? `In Watchlist: ${STATUS_CONFIG[currentStatus]?.label}. Click for options` : 'Add to Watchlist'}
        >
          {isBookmarked ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
        </button>

        {isOpen && (
          <div
            className="absolute right-0 bottom-full mb-2 w-44 rounded-xl bg-dark-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl p-1.5 z-40 animate-fade-in text-xs"
            role="menu"
            aria-label="Watchlist Status Menu"
          >
            <div className="px-2.5 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Watchlist Status
            </div>
            {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
              <button
                key={key}
                role="menuitem"
                onClick={(e) => handleSetStatus(key, e)}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left transition focus-visible:ring-1 focus-visible:ring-brand-400 focus-visible:outline-none ${
                  currentStatus === key
                    ? 'bg-brand-500/20 text-brand-300 font-medium'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <span>{cfg.label}</span>
                {currentStatus === key && <Check className="w-3.5 h-3.5 text-brand-400" />}
              </button>
            ))}
            {isBookmarked && (
              <div className="mt-1 pt-1 border-t border-slate-800">
                <button
                  role="menuitem"
                  onClick={handleRemove}
                  className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-left text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition focus-visible:ring-1 focus-visible:ring-rose-400 focus-visible:outline-none"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Remove</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Full button version (e.g. for Detail Page or Hero)
  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        onClick={toggleDropdown}
        disabled={loading}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all border shadow-sm focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
          isBookmarked
            ? 'bg-brand-600 hover:bg-brand-500 text-white border-brand-400/40 shadow-glow-sm'
            : 'bg-dark-850 hover:bg-dark-800 text-slate-200 border-slate-700/80'
        }`}
      >
        {isBookmarked ? (
          <>
            <BookmarkCheck className="w-4 h-4 text-white" />
            <span>{STATUS_CONFIG[currentStatus]?.label || 'In Watchlist'}</span>
          </>
        ) : (
          <>
            <Bookmark className="w-4 h-4 text-slate-400" />
            <span>Add to Watchlist</span>
          </>
        )}
        <ChevronDown className="w-3.5 h-3.5 ml-1 opacity-70" />
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full mt-2 w-48 rounded-xl bg-dark-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl p-1.5 z-40 animate-fade-in text-sm">
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Select Status
          </div>
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
            <button
              key={key}
              onClick={(e) => handleSetStatus(key, e)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition ${
                currentStatus === key
                  ? 'bg-brand-500/20 text-brand-300 font-medium'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span>{cfg.label}</span>
              {currentStatus === key && <Check className="w-4 h-4 text-brand-400" />}
            </button>
          ))}
          {isBookmarked && (
            <div className="mt-1.5 pt-1.5 border-t border-slate-800">
              <button
                onClick={handleRemove}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition"
              >
                <Trash2 className="w-4 h-4" />
                <span>Remove from Watchlist</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
