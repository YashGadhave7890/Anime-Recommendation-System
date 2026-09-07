import React, { useState } from 'react';
import { Filter, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';

const GENRES = [
  'Action',
  'Adventure',
  'Comedy',
  'Drama',
  'Fantasy',
  'Mystery',
  'Psychological',
  'Sci-Fi',
  'Shounen',
  'Slice of Life',
  'Supernatural',
  'Thriller',
  'Sports',
  'Romance',
  'Military',
  'Music',
  'Magic',
  'Horror',
];

const TYPES = ['TV', 'Movie', 'OVA', 'ONA', 'Special'];

const SORTS = [
  { label: 'Bayesian Quality', value: 'weighted_score' },
  { label: 'MAL Score', value: 'score' },
  { label: 'Most Popular', value: 'members' },
  { label: 'Release Year', value: 'release_year' },
  { label: 'Title (A-Z)', value: 'name' },
];

export default function FilterPanel({ filters, onChange, onReset }) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const hasActiveFilters = Boolean(
    filters.genre ||
      filters.type ||
      filters.min_score ||
      filters.sort_by !== 'weighted_score' ||
      filters.order !== 'desc'
  );

  return (
    <div className="p-4 sm:p-6 rounded-3xl bg-dark-900 border border-slate-700/80 shadow-lg space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-white font-bold text-sm sm:text-base">
            <Filter className="w-4 h-4 text-brand-400" />
            <span>Catalog Filters</span>
          </div>
          {hasActiveFilters && (
            <span className="px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 text-[10px] font-bold">
              Active
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none rounded-lg p-1"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}

          {/* Mobile Collapse Toggle Button */}
          <button
            onClick={() => setIsMobileOpen(!isMobileOpen)}
            className="sm:hidden flex items-center gap-1 px-2.5 py-1 rounded-lg bg-dark-850 border border-slate-700 text-xs text-slate-300"
            aria-expanded={isMobileOpen}
            aria-label="Toggle filter controls"
          >
            <span>{isMobileOpen ? 'Hide' : 'Show'} Filters</span>
            {isMobileOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Filter Controls (Collapsible on mobile, always visible on sm+) */}
      <div className={`grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 text-xs pt-2 border-t border-slate-800 ${
        isMobileOpen ? 'grid' : 'hidden sm:grid'
      }`}>
        {/* Genre Selector */}
        <div>
          <label htmlFor="filter-genre" className="block text-slate-300 font-semibold mb-1.5">
            Genre
          </label>
          <select
            id="filter-genre"
            value={filters.genre || ''}
            onChange={(e) => onChange('genre', e.target.value || null)}
            className="w-full px-3 py-2 rounded-xl bg-dark-850 border border-slate-700 text-slate-200 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            <option value="">All Genres</option>
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        {/* Format / Type Selector */}
        <div>
          <label htmlFor="filter-format" className="block text-slate-300 font-semibold mb-1.5">
            Format
          </label>
          <select
            id="filter-format"
            value={filters.type || ''}
            onChange={(e) => onChange('type', e.target.value || null)}
            className="w-full px-3 py-2 rounded-xl bg-dark-850 border border-slate-700 text-slate-200 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            <option value="">All Formats</option>
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Minimum Score */}
        <div>
          <label htmlFor="filter-min-score" className="block text-slate-300 font-semibold mb-1.5">
            Minimum Score
          </label>
          <select
            id="filter-min-score"
            value={filters.min_score || ''}
            onChange={(e) => onChange('min_score', e.target.value ? Number(e.target.value) : null)}
            className="w-full px-3 py-2 rounded-xl bg-dark-850 border border-slate-700 text-slate-200 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            <option value="">Any Score</option>
            <option value="8.5">8.5+ (Masterpiece)</option>
            <option value="8.0">8.0+ (Great)</option>
            <option value="7.5">7.5+ (Very Good)</option>
            <option value="7.0">7.0+ (Good)</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label htmlFor="filter-sort-by" className="block text-slate-300 font-semibold mb-1.5">
            Sort By
          </label>
          <select
            id="filter-sort-by"
            value={filters.sort_by || 'weighted_score'}
            onChange={(e) => onChange('sort_by', e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-dark-850 border border-slate-700 text-slate-200 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label htmlFor="filter-order" className="block text-slate-300 font-semibold mb-1.5">
            Order
          </label>
          <select
            id="filter-order"
            value={filters.order || 'desc'}
            onChange={(e) => onChange('order', e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-dark-850 border border-slate-700 text-slate-200 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          >
            <option value="desc">Descending (High to Low)</option>
            <option value="asc">Ascending (Low to High)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
