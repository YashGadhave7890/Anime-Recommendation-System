import React from 'react';
import AnimeCard from './AnimeCard';

export default function AnimeGrid({ items = [], recommendationKey = null }) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
      {items.map((anime, index) => (
        <AnimeCard
          key={anime.mal_id || anime.id || index}
          anime={anime}
          similarityScore={anime.similarity_score}
          hybridScore={anime.hybrid_score}
          recommendationReason={anime.recommendation_reason}
        />
      ))}
    </div>
  );
}
