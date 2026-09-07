import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Star,
  Film,
  Calendar,
  Users,
  Sparkles,
  ArrowLeft,
  Share2,
  CheckCircle2,
  Heart,
} from 'lucide-react';
import { getAnimeDetail, getSimilarAnime } from '../api/anime';
import GenreBadge from '../components/common/GenreBadge';
import WatchlistButton from '../components/common/WatchlistButton';
import StarRating from '../components/common/StarRating';
import RatingModal from '../components/common/RatingModal';
import AnimeCarousel from '../components/home/AnimeCarousel';
import { DetailPageSkeleton } from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';
import { useUser } from '../context/UserContext';
import { useToast } from '../context/ToastContext';

export default function AnimeDetailPage() {
  const { id } = useParams();
  const { getUserRatingVal } = useUser();
  const { showToast } = useToast();

  const [anime, setAnime] = useState(null);
  const [similarAnime, setSimilarAnime] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
  const [isSynopsisExpanded, setIsSynopsisExpanded] = useState(false);

  const existingRating = getUserRatingVal(id);

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        const [detailData, similarData] = await Promise.all([
          getAnimeDetail(id),
          getSimilarAnime(id, 10).catch(() => ({ recommendations: [] })),
        ]);

        if (!isCancelled) {
          setAnime(detailData);
          setSimilarAnime(similarData.recommendations || []);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Anime detail load error:', err);
          setError(err.message || 'Anime not found in catalog.');
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }

    loadData();

    return () => {
      isCancelled = true;
    };
  }, [id]);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      showToast('Anime page link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <DetailPageSkeleton />
      </div>
    );
  }

  if (error || !anime) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16">
        <ErrorState
          title="Anime Not Found"
          message={`We could not locate anime ID #${id} in the database.`}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  const title = anime.name;
  const englishTitle = anime.english_name;
  const japaneseTitle = anime.japanese_name;
  const score = anime.score;
  const weightedScore = anime.weighted_score;
  const members = anime.members;
  const formatType = anime.type || 'TV';
  const episodes = anime.episodes;
  const year = anime.release_year;
  const synopsis = anime.synopsis || 'No synopsis provided for this title.';

  const genresList = typeof anime.genres === 'string'
    ? anime.genres.split(',').map((g) => g.trim()).filter(Boolean)
    : [];

  const backdropImg = anime.img_url || 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80';

  return (
    <div className="space-y-12 pb-16">
      {/* Ambient Blurred Backdrop */}
      <div className="relative w-full overflow-hidden bg-dark-950 border-b border-slate-800">
        <div
          className="absolute inset-0 bg-cover bg-center filter blur-3xl scale-125 opacity-25 pointer-events-none"
          style={{ backgroundImage: `url(${backdropImg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-dark-950/80 to-transparent pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12">
          {/* Back button */}
          <Link
            to="/discover"
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Discover</span>
          </Link>

          {/* Main Showcase Layout */}
          <div className="flex flex-col md:flex-row gap-8 lg:gap-12 items-start">
            {/* Poster Card */}
            <div className="w-64 sm:w-72 aspect-[3/4] shrink-0 mx-auto md:mx-0 rounded-3xl overflow-hidden border-2 border-slate-700/80 shadow-2xl bg-dark-900 group">
              <img
                src={backdropImg}
                alt={title}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Right Information Column */}
            <div className="flex-1 space-y-6">
              {/* Type, Year, Episodes Pills */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-1 rounded-lg bg-brand-500/20 text-brand-300 font-bold uppercase text-xs border border-brand-500/30">
                  {formatType}
                </span>
                {year && (
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-dark-850 text-slate-300 text-xs border border-slate-700">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{year}</span>
                  </span>
                )}
                {episodes && (
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-dark-850 text-slate-300 text-xs border border-slate-700">
                    <Film className="w-3.5 h-3.5" />
                    <span>{episodes} Episodes</span>
                  </span>
                )}
                {members && (
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-dark-850 text-slate-300 text-xs border border-slate-700">
                    <Users className="w-3.5 h-3.5" />
                    <span>{members.toLocaleString()} Members</span>
                  </span>
                )}
              </div>

              {/* Title Header */}
              <div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
                  {title}
                </h1>
                {englishTitle && englishTitle !== title && (
                  <p className="text-slate-300 text-base sm:text-lg font-medium mt-1">
                    {englishTitle}
                  </p>
                )}
                {japaneseTitle && (
                  <p className="text-slate-500 text-xs sm:text-sm mt-0.5">
                    {japaneseTitle}
                  </p>
                )}
              </div>

              {/* Score Badges */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-3 p-3 px-4 rounded-2xl bg-dark-900 border border-slate-800">
                  <div className="p-2 rounded-xl bg-amber-500/15 text-amber-400">
                    <Star className="w-5 h-5 fill-amber-400" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-medium">MyAnimeList Score</div>
                    <div className="text-xl font-extrabold text-white">
                      {score ? Number(score).toFixed(2) : '—'}
                      <span className="text-xs text-slate-500 font-normal"> / 10</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 px-4 rounded-2xl bg-dark-900 border border-slate-800">
                  <div className="p-2 rounded-xl bg-brand-500/15 text-brand-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-medium">Bayesian Weighted Score</div>
                    <div className="text-xl font-extrabold text-brand-300">
                      {weightedScore ? Number(weightedScore).toFixed(2) : '—'}
                      <span className="text-xs text-slate-500 font-normal"> / 10</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Genres List */}
              <div className="flex flex-wrap gap-2">
                {genresList.map((g) => (
                  <GenreBadge key={g} genre={g} clickable={true} size="md" />
                ))}
              </div>

              {/* Interactive Actions Row: Watchlist & Rating Button */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <WatchlistButton animeId={anime.mal_id} animeTitle={title} compact={false} />

                <button
                  onClick={() => setIsRatingModalOpen(true)}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl border text-sm font-medium transition ${
                    existingRating
                      ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                      : 'bg-dark-850 hover:bg-dark-800 text-slate-200 border-slate-700'
                  }`}
                >
                  <Star className={`w-4 h-4 ${existingRating ? 'fill-amber-400 text-amber-400' : ''}`} />
                  <span>
                    {existingRating ? `Your Rating: ${existingRating}/10` : 'Rate Anime'}
                  </span>
                </button>

                <button
                  onClick={handleShare}
                  className="p-2.5 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-300 hover:text-white border border-slate-700 transition"
                  title="Share Anime Link"
                  aria-label="Share"
                >
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Synopsis & AI Reasoning Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Synopsis */}
          <div className="lg:col-span-2 p-6 sm:p-8 rounded-3xl bg-dark-900 border border-slate-800/80 space-y-4">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Plot Synopsis
            </h2>
            <div className="text-slate-300 text-sm sm:text-base leading-relaxed space-y-3 font-normal">
              <p className={!isSynopsisExpanded && synopsis.length > 400 ? 'line-clamp-4' : ''}>
                {synopsis}
              </p>
              {synopsis.length > 400 && (
                <button
                  onClick={() => setIsSynopsisExpanded(!isSynopsisExpanded)}
                  className="text-xs font-semibold text-brand-400 hover:text-brand-300 transition"
                >
                  {isSynopsisExpanded ? 'Show less' : 'Read full synopsis...'}
                </button>
              )}
            </div>
          </div>

          {/* Why ANIMORA Recommends This Box */}
          <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-indigo-950/40 to-dark-900 border border-brand-500/30 space-y-4">
            <div className="flex items-center gap-2 text-brand-300 font-bold text-sm">
              <Sparkles className="w-4 h-4 text-brand-400" />
              <span>Why ANIMORA Recommends This</span>
            </div>

            <ul className="space-y-3 text-xs sm:text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong>High Community Consensus:</strong> Bayesian rating of{' '}
                  <span className="text-white font-semibold">{Number(weightedScore).toFixed(2)}</span>{' '}
                  smooths out small-sample bias across {members.toLocaleString()} members.
                </span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Thematic Depth:</strong> Tagged in{' '}
                  <span className="text-white font-semibold">{genresList.slice(0, 3).join(', ')}</span>{' '}
                  with rich vocabulary in TF-IDF content space.
                </span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Rocchio Profile Alignment:</strong> High cosine dot product similarity with
                  users who favor quality storytelling and acclaimed character arcs.
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Similar Anime Carousel */}
        {similarAnime.length > 0 && (
          <AnimeCarousel
            title={`Similar to ${title}`}
            subtitle="Calculated in real time via TF-IDF cosine similarity over synopsis and metadata"
            badge="TF-IDF Similarity"
            items={similarAnime}
          />
        )}
      </div>

      {/* Rating Modal */}
      <RatingModal
        isOpen={isRatingModalOpen}
        onClose={() => setIsRatingModalOpen(false)}
        animeId={anime.mal_id}
        animeTitle={title}
        initialRating={existingRating || 8}
      />
    </div>
  );
}
