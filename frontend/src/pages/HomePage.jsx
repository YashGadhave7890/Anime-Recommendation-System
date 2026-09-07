import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Compass, Flame, Star, ArrowRight } from 'lucide-react';
import HeroBanner from '../components/home/HeroBanner';
import AnimeCarousel from '../components/home/AnimeCarousel';
import GenreQuickFilter from '../components/home/GenreQuickFilter';
import { HeroBannerSkeleton, AnimeCardSkeleton } from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';
import { getAnimeList, getAnimeDetail, getSimilarAnime } from '../api/anime';
import { getPopularRecommendations, getPersonalizedRecommendations } from '../api/recommendations';
import { useUser } from '../context/UserContext';

export default function HomePage() {
  const { userId } = useUser();
  const [heroAnime, setHeroAnime] = useState(null);
  const [trendingAnime, setTrendingAnime] = useState([]);
  const [personalizedAnime, setPersonalizedAnime] = useState([]);
  const [popularAnime, setPopularAnime] = useState([]);
  const [similarToFavorite, setSimilarToFavorite] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHomeData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch featured spotlight (Fullmetal Alchemist: Brotherhood, MAL ID: 5114)
      const spotlightPromise = getAnimeDetail(5114).catch(() => null);

      // Fetch Trending / Top Rated
      const trendingPromise = getAnimeList({
        sort_by: 'weighted_score',
        order: 'desc',
        limit: 12,
      }).then((res) => res.items).catch(() => []);

      // Fetch Personalized for active user
      const personalizedPromise = getPersonalizedRecommendations({
        top_n: 12,
      }).then((res) => res.recommendations).catch(() => []);

      // Fetch Popular baseline
      const popularPromise = getPopularRecommendations({
        top_n: 12,
      }).then((res) => res.recommendations).catch(() => []);

      // Fetch "Because you liked Death Note (MAL ID 1535)"
      const similarPromise = getSimilarAnime(1535, 12)
        .then((res) => res.recommendations)
        .catch(() => []);

      const [spotlight, trending, personalized, popular, similar] = await Promise.all([
        spotlightPromise,
        trendingPromise,
        personalizedPromise,
        popularPromise,
        similarPromise,
      ]);

      setHeroAnime(spotlight || (trending.length > 0 ? trending[0] : null));
      setTrendingAnime(trending);
      setPersonalizedAnime(personalized);
      setPopularAnime(popular);
      setSimilarToFavorite(similar);
    } catch (err) {
      console.error('Error loading home data:', err);
      setError(err.message || 'Failed to connect to ANIMORA recommendation backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHomeData();
  }, [userId]);

  if (error && !trendingAnime.length) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16">
        <ErrorState
          title="Backend Service Offline"
          message="Could not connect to the ANIMORA backend service. Please verify the API server is running and accessible."
          onRetry={fetchHomeData}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-12 sm:space-y-16">
      {/* Hero Section */}
      {loading ? (
        <HeroBannerSkeleton />
      ) : (
        heroAnime && <HeroBanner anime={heroAnime} />
      )}

      {/* Recommended For You Section */}
      <section>
        {loading ? (
          <div className="space-y-4">
            <div className="h-8 bg-slate-800 rounded w-64 animate-shimmer" />
            <div className="flex gap-4 overflow-hidden">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="w-52 shrink-0">
                  <AnimeCardSkeleton />
                </div>
              ))}
            </div>
          </div>
        ) : (
          personalizedAnime.length > 0 && (
            <AnimeCarousel
              title="Recommended For You"
              subtitle="Personalized recommendations tailored to your taste vectors and ratings"
              badge="Personalized ML"
              items={personalizedAnime}
              viewAllLink="/recommendations"
            />
          )
        )}
      </section>

      {/* Trending & Critically Acclaimed */}
      <section>
        {loading ? (
          <div className="space-y-4">
            <div className="h-8 bg-slate-800 rounded w-64 animate-shimmer" />
            <div className="flex gap-4 overflow-hidden">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="w-52 shrink-0">
                  <AnimeCardSkeleton />
                </div>
              ))}
            </div>
          </div>
        ) : (
          trendingAnime.length > 0 && (
            <AnimeCarousel
              title="Top Rated Masterpieces"
              subtitle="Ranked by Bayesian weighted scores over millions of community reviews"
              badge="Bayesian Quality"
              items={trendingAnime}
              viewAllLink="/discover?sort_by=weighted_score&order=desc"
            />
          )
        )}
      </section>

      {/* Genre Discovery Grid */}
      <GenreQuickFilter />

      {/* "Because You Liked Death Note" Section */}
      {similarToFavorite.length > 0 && (
        <section>
          <AnimeCarousel
            title="Because You Liked Death Note"
            subtitle="Content-based TF-IDF similarity over plot synopsis, psychological tags, and themes"
            badge="Content Soup Match"
            items={similarToFavorite}
            viewAllLink="/anime/1535"
          />
        </section>
      )}

      {/* Popular Baseline Section */}
      {popularAnime.length > 0 && (
        <section>
          <AnimeCarousel
            title="Popular Community Picks"
            subtitle="Most viewed and discussed titles across global anime communities"
            badge="Community Trend"
            items={popularAnime}
            viewAllLink="/discover?sort_by=members&order=desc"
          />
        </section>
      )}

      {/* CTA Discover Banner */}
      <section className="relative rounded-3xl overflow-hidden p-8 sm:p-12 bg-gradient-to-r from-brand-950 via-dark-900 to-violet-950 border border-brand-500/20 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="max-w-xl space-y-2 text-center sm:text-left">
          <span className="text-xs font-bold text-brand-400 uppercase tracking-wider">
            17,495 Anime Titles Indexed
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Looking for something specific?
          </h2>
          <p className="text-slate-300 text-sm">
            Search by title, filter by year, genre, format, or sort by Bayesian ratings.
          </p>
        </div>

        <Link
          to="/discover"
          className="shrink-0 flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-sm shadow-glow-sm hover:shadow-glow-md transition-all"
        >
          <Compass className="w-5 h-5" />
          <span>Explore Entire Catalog</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </section>
    </div>
  );
}
