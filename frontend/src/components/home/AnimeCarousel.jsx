import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';
import AnimeCard from '../common/AnimeCard';

export default function AnimeCarousel({
  title,
  subtitle = null,
  badge = null,
  items = [],
  viewAllLink = null,
}) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollAmount = clientWidth * 0.75;
      scrollRef.current.scrollTo({
        left: direction === 'left' ? scrollLeft - scrollAmount : scrollLeft + scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  if (!items || items.length === 0) return null;

  return (
    <section className="space-y-4">
      {/* Section Header */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {badge && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-brand-500/15 border border-brand-500/30 text-brand-300 text-[11px] font-semibold uppercase tracking-wider">
                <Sparkles className="w-3 h-3 text-brand-400" />
                <span>{badge}</span>
              </span>
            )}
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {title}
            </h2>
          </div>
          {subtitle && <p className="text-xs sm:text-sm text-slate-400">{subtitle}</p>}
        </div>

        {/* Carousel Navigation Arrows */}
        <div className="flex items-center gap-2">
          {viewAllLink && (
            <a
              href={viewAllLink}
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 mr-2 transition"
            >
              View all →
            </a>
          )}
          <button
            onClick={() => scroll('left')}
            className="p-2 rounded-xl bg-dark-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
            aria-label="Scroll carousel left"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => scroll('right')}
            className="p-2 rounded-xl bg-dark-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
            aria-label="Scroll carousel right"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Horizontal Scroll Track */}
      <div
        ref={scrollRef}
        className="flex gap-4 sm:gap-5 overflow-x-auto pb-4 pt-1 scrollbar-none snap-x snap-mandatory scroll-smooth"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {items.map((anime, index) => (
          <div
            key={anime.mal_id || anime.id || index}
            className="w-40 sm:w-48 lg:w-52 shrink-0 snap-start"
          >
            <AnimeCard
              anime={anime}
              similarityScore={anime.similarity_score}
              hybridScore={anime.hybrid_score}
              recommendationReason={anime.recommendation_reason}
            />
          </div>
        ))}
      </div>
    </section>
  );
}
