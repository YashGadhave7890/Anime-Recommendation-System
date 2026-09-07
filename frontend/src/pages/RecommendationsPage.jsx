import React, { useState, useEffect } from 'react';
import { Sparkles, Sliders, Compass, Cpu, HelpCircle, Layers, Flame } from 'lucide-react';
import AnimeGrid from '../components/common/AnimeGrid';
import { AnimeGridSkeleton } from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';
import HybridWeightSliders from '../components/recommendations/HybridWeightSliders';
import ColdStartBanner from '../components/recommendations/ColdStartBanner';
import { getPersonalizedRecommendations, getPopularRecommendations } from '../api/recommendations';
import { useUser } from '../context/UserContext';

export default function RecommendationsPage() {
  const { userId, currentUser, ratings } = useUser();
  const [activeTab, setActiveTab] = useState('personalized'); // 'personalized' | 'popular'
  const [items, setItems] = useState([]);
  const [strategy, setStrategy] = useState('personalized');
  const [weightsUsed, setWeightsUsed] = useState({ content: 0.0, user: 0.7, popularity: 0.3 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRecommendations = async (customWeights = null) => {
    try {
      setLoading(true);
      setError(null);

      if (activeTab === 'popular') {
        const data = await getPopularRecommendations({ top_n: 24 });
        setItems(data.recommendations || []);
        setStrategy(data.strategy);
      } else {
        const params = {
          top_n: 24,
        };
        if (customWeights) {
          params.w_content = customWeights.content;
          params.w_user = customWeights.user;
          params.w_pop = customWeights.popularity;
        }

        const data = await getPersonalizedRecommendations(params);
        setItems(data.recommendations || []);
        setStrategy(data.strategy);
        if (data.weights_used) {
          setWeightsUsed(data.weights_used);
        }
      }
    } catch (err) {
      console.error('Recommendations load error:', err);
      setError(err.message || 'Failed to fetch recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [userId, activeTab]);

  const isColdStartActive = strategy === 'cold_start_tier1' || strategy === 'cold_start_tier2' || ratings.length === 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Header Banner */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold">
          <Cpu className="w-3.5 h-3.5 text-brand-400" />
          <span>Machine Learning Recommendation Showcase</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Personalized Anime Feed
        </h1>
        <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
          Powered by a hybrid ranking engine blending <strong>Rocchio user taste profiles</strong>,{' '}
          <strong>TF-IDF content soup cosine similarity</strong>, and{' '}
          <strong>Bayesian community quality baselines</strong> over 17,495 anime titles.
        </p>
      </div>

      {/* Persona Context Badge */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-dark-900 border border-slate-800 text-xs sm:text-sm">
        <div className="flex items-center gap-3">
          <img
            src={currentUser.avatar}
            alt={currentUser.displayName}
            className="w-10 h-10 rounded-xl object-cover border border-brand-500/40"
          />
          <div>
            <div className="font-semibold text-white flex items-center gap-2">
              <span>Browsing as: {currentUser.displayName}</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                  isColdStartActive
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}
              >
                Strategy: {strategy}
              </span>
            </div>
            <div className="text-slate-400 text-xs mt-0.5">
              {ratings.length > 0
                ? `${ratings.length} anime rated in taste vector`
                : 'No ratings yet (demonstrating two-tier cold start)'}
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 rounded-xl bg-dark-850 border border-slate-800">
          <button
            onClick={() => setActiveTab('personalized')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'personalized'
                ? 'bg-brand-600 text-white shadow-glow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Hybrid Personalized</span>
          </button>
          <button
            onClick={() => setActiveTab('popular')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'popular'
                ? 'bg-brand-600 text-white shadow-glow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>Popular Baseline</span>
          </button>
        </div>
      </div>

      {/* Cold Start Banner if user has 0 ratings */}
      {isColdStartActive && activeTab === 'personalized' && (
        <ColdStartBanner onPreferencesSaved={() => fetchRecommendations()} />
      )}

      {/* Live Hybrid Weight Tuning Sliders */}
      {activeTab === 'personalized' && !isColdStartActive && (
        <HybridWeightSliders
          initialWeights={weightsUsed}
          onApply={(newWeights) => fetchRecommendations(newWeights)}
          loading={loading}
        />
      )}

      {/* Recommendations Grid */}
      <section className="space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>
              {activeTab === 'personalized'
                ? isColdStartActive
                  ? 'Cold-Start Baseline Recommendations'
                  : 'Tailored For Your Taste'
                : 'Most Popular Across Anime Communities'}
            </span>
          </h2>
          <span className="text-xs text-slate-400 font-medium">
            {items.length} titles generated
          </span>
        </div>

        {loading ? (
          <AnimeGridSkeleton count={18} />
        ) : error ? (
          <ErrorState
            title="Failed to Load Recommendations"
            message={error}
            onRetry={() => fetchRecommendations()}
          />
        ) : (
          <AnimeGrid items={items} />
        )}
      </section>
    </div>
  );
}
