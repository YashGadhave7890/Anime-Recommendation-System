import React from 'react';
import { useNavigate } from 'react-router-dom';

const GENRE_COLORS = {
  Action: 'bg-red-500/10 text-red-300 border-red-500/20 hover:border-red-500/40',
  Adventure: 'bg-amber-500/10 text-amber-300 border-amber-500/20 hover:border-amber-500/40',
  Comedy: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20 hover:border-emerald-500/40',
  Drama: 'bg-blue-500/10 text-blue-300 border-blue-500/20 hover:border-blue-500/40',
  Fantasy: 'bg-purple-500/10 text-purple-300 border-purple-500/20 hover:border-purple-500/40',
  Mystery: 'bg-violet-500/10 text-violet-300 border-violet-500/20 hover:border-violet-500/40',
  Psychological: 'bg-rose-500/10 text-rose-300 border-rose-500/20 hover:border-rose-500/40',
  'Sci-Fi': 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20 hover:border-cyan-500/40',
  Thriller: 'bg-fuchsia-500/10 text-fuchsia-300 border-fuchsia-500/20 hover:border-fuchsia-500/40',
  'Slice of Life': 'bg-teal-500/10 text-teal-300 border-teal-500/20 hover:border-teal-500/40',
  Supernatural: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20 hover:border-indigo-500/40',
};

export default function GenreBadge({ genre, clickable = false, size = 'sm' }) {
  const navigate = useNavigate();
  const cleanGenre = (genre || '').trim();
  const colorClass =
    GENRE_COLORS[cleanGenre] ||
    'bg-slate-800/60 text-slate-300 border-slate-700/50 hover:border-slate-600';

  const sizeClass =
    size === 'xs'
      ? 'text-[10px] px-1.5 py-0.5'
      : size === 'md'
      ? 'text-xs px-3 py-1 font-medium'
      : 'text-xs px-2 py-0.5';

  const handleClick = (e) => {
    if (clickable) {
      e.stopPropagation();
      navigate(`/discover?genre=${encodeURIComponent(cleanGenre)}`);
    }
  };

  return (
    <span
      onClick={handleClick}
      className={`inline-block rounded-md border font-normal transition-all duration-200 ${sizeClass} ${colorClass} ${
        clickable ? 'cursor-pointer' : ''
      }`}
    >
      {cleanGenre}
    </span>
  );
}
