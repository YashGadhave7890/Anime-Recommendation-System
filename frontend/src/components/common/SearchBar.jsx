import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Film, Star, Loader2, ArrowRight } from 'lucide-react';
import { searchAnime } from '../../api/anime';

export default function SearchBar({
  placeholder = 'Search 17,500+ anime titles...',
  initialQuery = '',
  onSearch = null,
  showDropdown = true,
  className = '',
}) {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  // Keep query in sync if initialQuery changes from outside
  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  // Debounced auto-complete search
  useEffect(() => {
    if (!showDropdown) return;

    if (!query || query.trim().length < 2) {
      setResults([]);
      setIsOpen(false);
      setSelectedIndex(-1);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const data = await searchAnime(query.trim(), 6);
        setResults(data);
        setIsOpen(true);
        setSelectedIndex(-1);
      } catch (err) {
        console.warn('Search autocomplete failed:', err);
      } finally {
        setLoading(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [query, showDropdown]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleKeyDown = (e) => {
    if (!isOpen || results.length === 0) {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        e.preventDefault();
        handleSelectAnime(results[selectedIndex].mal_id);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
      setSelectedIndex(-1);
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (selectedIndex >= 0 && selectedIndex < results.length) {
      handleSelectAnime(results[selectedIndex].mal_id);
      return;
    }
    if (!query || !query.trim()) return;
    setIsOpen(false);
    setSelectedIndex(-1);

    if (onSearch) {
      onSearch(query.trim());
    } else {
      navigate(`/discover?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    setSelectedIndex(-1);
    if (onSearch) onSearch('');
  };

  const handleSelectAnime = (malId) => {
    setIsOpen(false);
    setSelectedIndex(-1);
    navigate(`/anime/${malId}`);
  };

  return (
    <div className={`relative w-full ${className}`} ref={containerRef}>
      <form onSubmit={handleSubmit} className="relative flex items-center" role="search">
        <div className="absolute left-4 pointer-events-none text-slate-400">
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin text-brand-400" />
          ) : (
            <Search className="w-5 h-5" />
          )}
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim().length >= 2 && results.length > 0 && setIsOpen(true)}
          placeholder={placeholder}
          role="combobox"
          aria-expanded={isOpen}
          aria-autocomplete="list"
          aria-label={placeholder}
          className="w-full pl-12 pr-10 py-3 rounded-2xl bg-dark-900/90 border border-slate-700/80 hover:border-slate-600 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 text-slate-100 placeholder-slate-400 text-sm shadow-inner transition-all backdrop-blur-md outline-none"
        />

        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3.5 p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/10 transition focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
            aria-label="Clear search query"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </form>

      {/* Auto-complete Dropdown */}
      {showDropdown && isOpen && (
        <div
          className="absolute left-0 right-0 top-full mt-2 rounded-2xl bg-dark-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl p-2 z-50 animate-fade-in overflow-hidden"
          role="listbox"
          aria-label="Search suggestions"
        >
          {results.length > 0 ? (
            <div>
              <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-slate-800/80 mb-1">
                <span>Top Matches</span>
                <span className="text-brand-400">17.5k Database</span>
              </div>
              <div className="space-y-1">
                {results.map((item, idx) => (
                  <div
                    key={item.mal_id}
                    role="option"
                    aria-selected={idx === selectedIndex}
                    onClick={() => handleSelectAnime(item.mal_id)}
                    className={`flex items-center gap-3 p-2 rounded-xl cursor-pointer transition group ${
                      idx === selectedIndex
                        ? 'bg-brand-500/20 border border-brand-500/40 text-white'
                        : 'hover:bg-white/5 text-slate-200'
                    }`}
                  >
                    <img
                      src={item.img_url || 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=100&auto=format&fit=crop&q=80'}
                      alt={item.name}
                      className="w-10 h-14 object-cover rounded-lg bg-dark-950 shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-slate-200 group-hover:text-brand-300 truncate">
                        {item.name}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                        <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-slate-300 uppercase">
                          {item.type || 'TV'}
                        </span>
                        {item.score && (
                          <span className="flex items-center gap-0.5 text-amber-400 font-medium">
                            <Star className="w-3 h-3 fill-amber-400" />
                            {Number(item.score).toFixed(1)}
                          </span>
                        )}
                        {item.release_year && <span>• {item.release_year}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* View all search results link */}
              <div
                onClick={handleSubmit}
                className="mt-1 pt-2 border-t border-slate-800/80 px-3 py-2 flex items-center justify-between text-xs font-semibold text-brand-400 hover:text-brand-300 cursor-pointer rounded-lg hover:bg-brand-500/10 transition"
              >
                <span>View all search results for &quot;{query}&quot;</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ) : (
            !loading && (
              <div className="p-4 text-center text-xs text-slate-400">
                No matching anime titles found. Press Enter to search catalog.
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
