import React, { useState } from 'react';
import { Sliders, RefreshCw, Cpu, Sparkles } from 'lucide-react';

export default function HybridWeightSliders({ initialWeights, onApply, loading = false }) {
  const [weights, setWeights] = useState({
    content: initialWeights?.content ?? 0.0,
    user: initialWeights?.user ?? 0.7,
    popularity: initialWeights?.popularity ?? 0.3,
  });

  const handleSliderChange = (key, value) => {
    setWeights((prev) => ({
      ...prev,
      [key]: parseFloat(value),
    }));
  };

  const applyPreset = (content, user, pop) => {
    const newWeights = { content, user, popularity: pop };
    setWeights(newWeights);
    onApply(newWeights);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onApply(weights);
  };

  // Calculate sum for normalization display
  const total = weights.content + weights.user + weights.popularity || 1.0;
  const pctContent = Math.round((weights.content / total) * 100);
  const pctUser = Math.round((weights.user / total) * 100);
  const pctPop = Math.round((weights.popularity / total) * 100);

  return (
    <div className="p-6 rounded-3xl bg-dark-900 border border-slate-700/80 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-brand-500/15 border border-brand-500/30 text-brand-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>Hybrid ML Weight Tuning</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
                Live Formula
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Customize the linear ranker blend: Score = (w_c · S_content) + (w_u · S_user) + (w_p · S_pop)
            </p>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => applyPreset(0.0, 0.7, 0.3)}
            className="px-2.5 py-1 rounded-lg bg-dark-850 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300 transition"
          >
            Taste Driven
          </button>
          <button
            type="button"
            onClick={() => applyPreset(0.4, 0.4, 0.2)}
            className="px-2.5 py-1 rounded-lg bg-dark-850 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300 transition"
          >
            Hybrid Balanced
          </button>
          <button
            type="button"
            onClick={() => applyPreset(0.1, 0.2, 0.7)}
            className="px-2.5 py-1 rounded-lg bg-dark-850 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300 transition"
          >
            Critically Acclaimed
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* User Profile Weight */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <label htmlFor="slider-user-taste" className="text-xs font-semibold text-slate-200">
                User Taste (Rocchio)
              </label>
              <span className="text-xs font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-md">
                {pctUser}%
              </span>
            </div>
            <input
              id="slider-user-taste"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={weights.user}
              aria-label="User taste profile weight"
              aria-valuemin="0"
              aria-valuemax="1"
              aria-valuenow={weights.user}
              onChange={(e) => handleSliderChange('user', e.target.value)}
              className="w-full accent-brand-500 cursor-pointer h-2 bg-slate-700 rounded-lg appearance-none focus-visible:ring-2 focus-visible:ring-brand-500"
            />
            <p className="text-[11px] text-slate-400 leading-tight">
              Personalized preference vector based on your rated favorites.
            </p>
          </div>

          {/* Content Similarity Weight */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <label htmlFor="slider-content-soup" className="text-xs font-semibold text-slate-200">
                Content Soup (TF-IDF)
              </label>
              <span className="text-xs font-bold text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded-md">
                {pctContent}%
              </span>
            </div>
            <input
              id="slider-content-soup"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={weights.content}
              aria-label="Content soup similarity weight"
              aria-valuemin="0"
              aria-valuemax="1"
              aria-valuenow={weights.content}
              onChange={(e) => handleSliderChange('content', e.target.value)}
              className="w-full accent-violet-500 cursor-pointer h-2 bg-slate-700 rounded-lg appearance-none focus-visible:ring-2 focus-visible:ring-violet-500"
            />
            <p className="text-[11px] text-slate-400 leading-tight">
              Direct cosine similarity over synopsis, genres, and studio tags.
            </p>
          </div>

          {/* Popularity / Bayesian Baseline */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <label htmlFor="slider-bayesian-pop" className="text-xs font-semibold text-slate-200">
                Bayesian Quality (WR)
              </label>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">
                {pctPop}%
              </span>
            </div>
            <input
              id="slider-bayesian-pop"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={weights.popularity}
              aria-label="Bayesian quality weight"
              aria-valuemin="0"
              aria-valuemax="1"
              aria-valuenow={weights.popularity}
              onChange={(e) => handleSliderChange('popularity', e.target.value)}
              className="w-full accent-emerald-500 cursor-pointer h-2 bg-slate-700 rounded-lg appearance-none focus-visible:ring-2 focus-visible:ring-emerald-500"
            />
            <p className="text-[11px] text-slate-400 leading-tight">
              Prior weight over 17,500 titles (m = 41,106 community votes).
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Cpu className="w-4 h-4" />
            )}
            <span>Apply Weights &amp; Re-Rank</span>
          </button>
        </div>
      </form>
    </div>
  );
}
