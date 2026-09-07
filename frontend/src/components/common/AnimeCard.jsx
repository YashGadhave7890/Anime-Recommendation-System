import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Star, Film, Sparkles } from 'lucide-react';
import WatchlistButton from './WatchlistButton';
import GenreBadge from './GenreBadge';

export default function AnimeCard({
  anime,
  recommendationReason = null,
  similarityScore = null,
  hybridScore = null,
}) {
  const [imgError, setImgError] = useState(false);

  const malId = anime.mal_id || anime.id;
  const title = anime.name || anime.title || 'Untitled Anime';
  const displayScore = anime.score || anime.weighted_score;
  const formatType = anime.type || 'TV';
  const year = anime.release_year || (anime.aired ? anime.aired.split(',')[1]?.trim() : null);

  // Extract first 1 or 2 genres
  const genresList = typeof anime.genres === 'string'
    ? anime.genres.split(',').map((g) => g.trim()).filter(Boolean)
    : Array.isArray(anime.genres)
    ? anime.genres
    : [];

  const firstGenre = genresList[0] || null;

  // Inline SVG fallback poster guaranteed to load offline and instantly
  const fallbackImg =
    "data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20300%20400%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22g%22%20x1%3D%220%25%22%20y1%3D%220%25%22%20x2%3D%22100%25%22%20y2%3D%22100%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23161f36%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%230b0f19%22%2F%3E%3C%2FlinearGradient%3E%3C%2Fdefs%3E%3Crect%20width%3D%22100%25%22%20height%3D%22100%25%22%20fill%3D%22url(%23g)%22%2F%3E%3Ccircle%20cx%3D%22150%22%20cy%3D%22170%22%20r%3D%2240%22%20fill%3D%22%23222d4a%22%2F%3E%3Cpolygon%20points%3D%22140%2C155%20165%2C170%20140%2C185%22%20fill%3D%22%236366f1%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%22240%22%20fill%3D%22%23818cf8%22%20font-size%3D%2214%22%20font-weight%3D%22bold%22%20font-family%3D%22system-ui%22%20text-anchor%3D%22middle%22%3EANIMORA%3C%2Ftext%3E%3C%2Fsvg%3E";

  return (
    <div className="group relative rounded-2xl bg-dark-900 border border-slate-800/80 hover:border-brand-500/40 transition-all duration-300 overflow-hidden flex flex-col hover:-translate-y-1.5 hover:shadow-glow-md">
      {/* Poster Image Container */}
      <Link
        to={`/anime/${malId}`}
        className="relative block aspect-[3/4] overflow-hidden bg-dark-950 focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:outline-none"
        aria-label={`View details for ${title}`}
      >
        <img
          src={!imgError && anime.img_url ? anime.img_url : fallbackImg}
          alt={title}
          onError={() => setImgError(true)}
          loading="lazy"
          decoding="async"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
        />

        {/* Ambient Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-black/30 opacity-80 group-hover:opacity-60 transition-opacity" />

        {/* Top Badges */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none">
          <span className="px-2 py-0.5 rounded-md bg-dark-950/85 backdrop-blur-md border border-white/10 text-[11px] font-semibold text-slate-200 uppercase tracking-wider">
            {formatType}
          </span>

          {/* Quick Watchlist Action */}
          <div className="pointer-events-auto">
            <WatchlistButton animeId={malId} animeTitle={title} compact={true} />
          </div>
        </div>

        {/* Recommendation Match Badge (if provided) */}
        {(similarityScore !== null || hybridScore !== null || recommendationReason) && (
          <div className="absolute bottom-2.5 left-2.5 right-2.5 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-950/90 border border-brand-400/40 text-brand-200 text-[11px] font-medium backdrop-blur-md">
            <Sparkles className="w-3 h-3 text-brand-400 shrink-0" />
            <span className="truncate">
              {recommendationReason ||
                (hybridScore
                  ? `${Math.round(hybridScore * 100)}% Match`
                  : `${Math.round(similarityScore * 100)}% Match`)}
            </span>
          </div>
        )}
      </Link>

      {/* Card Details */}
      <div className="p-3.5 flex-1 flex flex-col justify-between">
        <div>
          <Link
            to={`/anime/${malId}`}
            className="block font-semibold text-sm text-slate-100 group-hover:text-brand-300 transition-colors line-clamp-2 min-h-[2.5rem] leading-snug focus-visible:underline focus-visible:outline-none"
            title={title}
          >
            {title}
          </Link>

          {/* Genre & Year info */}
          <div className="flex items-center gap-1.5 mt-1.5 text-xs text-slate-400">
            {firstGenre && <GenreBadge genre={firstGenre} size="xs" clickable={true} />}
            {year && <span>• {year}</span>}
          </div>
        </div>

        {/* Footer info: Score & Episodes */}
        <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-800/60 text-xs">
          <div className="flex items-center gap-1 text-amber-400 font-semibold">
            <Star className="w-3.5 h-3.5 fill-amber-400" />
            <span>{displayScore ? Number(displayScore).toFixed(1) : '—'}</span>
          </div>

          <div className="flex items-center gap-1 text-slate-400">
            <Film className="w-3 h-3" />
            <span>{anime.episodes ? `${anime.episodes} eps` : 'Ongoing'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
