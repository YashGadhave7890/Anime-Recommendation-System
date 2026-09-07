import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Compass, Search, Filter, RefreshCw } from 'lucide-react';
import AnimeGrid from '../components/common/AnimeGrid';
import { AnimeGridSkeleton } from '../components/common/LoadingSkeleton';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import FilterPanel from '../components/discover/FilterPanel';
import Pagination from '../components/discover/Pagination';
import SearchBar from '../components/common/SearchBar';
import { getAnimeList, searchAnime } from '../api/anime';

export default function DiscoverPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Search & Filter State derived from URL
  const queryParam = searchParams.get('q') || '';
  const genreParam = searchParams.get('genre') || '';
  const typeParam = searchParams.get('type') || '';
  const minScoreParam = searchParams.get('min_score') || '';
  const sortByParam = searchParams.get('sort_by') || 'weighted_score';
  const orderParam = searchParams.get('order') || 'desc';
  const pageParam = parseInt(searchParams.get('page') || '1', 10);

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const filters = {
    genre: genreParam,
    type: typeParam,
    min_score: minScoreParam,
    sort_by: sortByParam,
    order: orderParam,
  };

  const updateFilters = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, String(value));
    } else {
      newParams.delete(key);
    }
    newParams.set('page', '1'); // Reset to page 1 on filter change
    setSearchParams(newParams);
  };

  const handleSearchSubmit = (term) => {
    const newParams = new URLSearchParams(searchParams);
    if (term) {
      newParams.set('q', term);
    } else {
      newParams.delete('q');
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const handleResetFilters = () => {
    setSearchParams({});
  };

  const handlePageChange = (newPage) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', String(newPage));
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    let isCancelled = false;

    async function loadCatalog() {
      try {
        setLoading(true);
        setError(null);

        // If a direct search query is present, check search results
        if (queryParam.trim()) {
          const searchResults = await searchAnime(queryParam.trim(), 40);
          if (!isCancelled) {
            setItems(searchResults);
            setTotal(searchResults.length);
            setTotalPages(1);
          }
        } else {
          // Standard filtered catalog request
          const data = await getAnimeList({
            page: pageParam,
            limit: 24,
            genre: genreParam || undefined,
            type: typeParam || undefined,
            min_score: minScoreParam ? parseFloat(minScoreParam) : undefined,
            sort_by: sortByParam,
            order: orderParam,
          });

          if (!isCancelled) {
            setItems(data.items);
            setTotal(data.total);
            setTotalPages(data.total_pages);
          }
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Discover load error:', err);
          setError(err.message || 'Failed to fetch catalog.');
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }

    loadCatalog();

    return () => {
      isCancelled = true;
    };
  }, [queryParam, genreParam, typeParam, minScoreParam, sortByParam, orderParam, pageParam]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-brand-400 text-xs font-bold uppercase tracking-wider">
          <Compass className="w-4 h-4" />
          <span>Catalog Explorer</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Discover Anime
        </h1>
        <p className="text-slate-400 text-sm max-w-xl">
          Search and filter across 17,495 anime titles using genre, format, Bayesian weighted scores, and release years.
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="max-w-2xl">
        <SearchBar
          placeholder="Filter by title, keywords, or English name..."
          initialQuery={queryParam}
          onSearch={handleSearchSubmit}
          showDropdown={false}
        />
      </div>

      {/* Filter Drawer / Panel */}
      {!queryParam && (
        <FilterPanel
          filters={filters}
          onChange={updateFilters}
          onReset={handleResetFilters}
        />
      )}

      {/* Search active notification */}
      {queryParam && (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-brand-500/10 border border-brand-500/30 text-xs sm:text-sm text-brand-200">
          <span>
            Showing search matches for &quot;<strong>{queryParam}</strong>&quot; ({total} found)
          </span>
          <button
            onClick={() => handleSearchSubmit('')}
            className="text-white hover:underline font-semibold"
          >
            Clear Search
          </button>
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
        <span>
          Showing {items.length} of {total.toLocaleString()} anime titles
        </span>
        {totalPages > 1 && (
          <span>
            Page {pageParam} of {totalPages}
          </span>
        )}
      </div>

      {/* Content Rendering */}
      {loading ? (
        <AnimeGridSkeleton count={24} />
      ) : error ? (
        <ErrorState
          title="Failed to Load Catalog"
          message={error}
          onRetry={() => window.location.reload()}
        />
      ) : items.length === 0 ? (
        <EmptyState
          title="No Matching Anime Found"
          description="We couldn't find any anime matching your current search or filter combination. Try clearing some filters."
          actionLabel="Clear All Filters"
          actionTo="/discover"
        />
      ) : (
        <>
          <AnimeGrid items={items} />

          {/* Pagination */}
          {!queryParam && totalPages > 1 && (
            <Pagination
              currentPage={pageParam}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </div>
  );
}
