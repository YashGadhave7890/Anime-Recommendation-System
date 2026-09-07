import React from 'react';
import { Sparkles, Heart, Database, Cpu, Layers } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-24 border-t border-slate-800/80 bg-dark-950/80 text-slate-400 py-12 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-violet-500 flex items-center justify-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="font-extrabold text-white text-base">ANIMORA</span>
              <p className="text-xs text-slate-500">Discover what you&apos;ll love next.</p>
            </div>
          </div>

          {/* Tech Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-900 border border-slate-800 text-xs text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-brand-400" />
              <span>FastAPI &amp; Scikit-Learn</span>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-900 border border-slate-800 text-xs text-slate-300">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              <span>17,495 Real MAL Records</span>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-900 border border-slate-800 text-xs text-slate-300">
              <Layers className="w-3.5 h-3.5 text-violet-400" />
              <span>Rocchio &amp; TF-IDF Hybrid</span>
            </span>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>
            Built as a portfolio-grade machine learning full-stack project. Anime data sourced from MyAnimeList.
          </p>
          <div className="flex items-center gap-1">
            <span>Crafted with</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
            <span>for anime enthusiasts.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
