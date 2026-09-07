import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Play, Sparkles } from 'lucide-react';
import GenreBadge from '../common/GenreBadge';
import WatchlistButton from '../common/WatchlistButton';

export default function HeroBanner({ anime }) {
  if (!anime) return null;

  const malId = anime.mal_id || anime.id;
  const title = anime.name || anime.title;
  const englishTitle = anime.english_name;
  const score = anime.score || anime.weighted_score;
  const year = anime.release_year;
  const type = anime.type || 'TV';
  const synopsis = anime.synopsis || 'An acclaimed masterpiece in the ANIMORA catalog.';

  const genres = typeof anime.genres === 'string'
    ? anime.genres.split(',').map((g) => g.trim()).slice(0, 4)
    : [];

  const backdropImg = anime.img_url || 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80';

  return (
    <div className="relative w-full rounded-3xl overflow-hidden border border-slate-800/80 shadow-2xl bg-dark-950">
      {/* Background Ambient Blur Image */}
      <div
        className="absolute inset-0 bg-cover bg-center filter blur-xl scale-110 opacity-30 pointer-events-none"
        style={{ backgroundImage: `url(${backdropImg})` }}
      />

      {/* Dark Gradient Mask */}
      <div className="absolute inset-0 bg-gradient-to-r from-dark-950 via-dark-950/90 to-dark-950/40 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent pointer-events-none" />

      {/* Content Container */}
      <div className="relative z-10 p-6 sm:p-10 lg:p-14 flex flex-col lg:flex-row items-center justify-between gap-8 min-h-[480px]">
        {/* Left Info Column */}
        <div className="max-w-2xl space-y-4 text-center lg:text-left">
          {/* Spotlight Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Featured Spotlight • High Bayesian Score</span>
          </div>

          {/* Titles */}
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
              {title}
            </h1>
            {englishTitle && englishTitle !== title && (
              <p className="text-slate-400 text-sm sm:text-base mt-1 font-medium">
                {englishTitle}
              </p>
            )}
          </div>

          {/* Metadata Row */}
          <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 text-xs sm:text-sm text-slate-300">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-300 font-bold border border-amber-500/20">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span>{score ? Number(score).toFixed(2) : '9.17'} MAL</span>
            </div>
            <span className="px-2.5 py-1 rounded-lg bg-dark-900 border border-slate-700 text-slate-300 font-medium uppercase text-xs">
              {type}
            </span>
            {year && <span>Released: {year}</span>}
            {anime.members && <span>• {(anime.members).toLocaleString()} Members</span>}
          </div>

          {/* Genre Badges */}
          <div className="flex flex-wrap items-center justify-center lg:justify-start gap-1.5 pt-1">
            {genres.map((g) => (
              <GenreBadge key={g} genre={g} clickable={true} size="md" />
            ))}
          </div>

          {/* Synopsis Excerpt */}
          <p className="text-slate-300 text-sm sm:text-base line-clamp-3 leading-relaxed max-w-xl">
            {synopsis}
          </p>

          {/* CTA Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-3 w-full">
            <Link
              to={`/anime/${malId}`}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-brand-600 to-violet-600 hover:from-brand-500 hover:to-violet-500 text-white font-semibold text-sm shadow-glow-sm hover:shadow-glow-md transition-all focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:outline-none"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>View Anime Details</span>
            </Link>

            <div className="w-full sm:w-auto flex justify-center">
              <WatchlistButton animeId={malId} animeTitle={title} compact={false} />
            </div>
          </div>
        </div>

        {/* Right Poster Artwork */}
        <div className="relative shrink-0 hidden sm:block">
          <div className="w-56 sm:w-64 aspect-[3/4] rounded-2xl overflow-hidden shadow-2xl border-2 border-white/10 group-hover:border-brand-500/50 transition-all duration-300 transform lg:rotate-2 hover:rotate-0">
            <img
              src={backdropImg}
              alt={title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="absolute -bottom-3 -right-3 px-3 py-1.5 rounded-xl bg-dark-900/90 border border-brand-500/40 backdrop-blur-md shadow-lg text-xs font-semibold text-brand-300 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>AI Verified Classic</span>
          </div>
        </div>
      </div>
    </div>
  );
}
