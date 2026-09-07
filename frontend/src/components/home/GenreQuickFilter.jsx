import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, Brain, Rocket, Smile, Sparkles, Heart, Compass, Eye, Zap, Shield } from 'lucide-react';

const TOP_GENRES = [
  { name: 'Action', icon: Flame, color: 'from-red-600/30 to-orange-600/10 border-red-500/30 text-red-300' },
  { name: 'Psychological', icon: Brain, color: 'from-rose-600/30 to-pink-600/10 border-rose-500/30 text-rose-300' },
  { name: 'Sci-Fi', icon: Rocket, color: 'from-cyan-600/30 to-blue-600/10 border-cyan-500/30 text-cyan-300' },
  { name: 'Comedy', icon: Smile, color: 'from-emerald-600/30 to-teal-600/10 border-emerald-500/30 text-emerald-300' },
  { name: 'Fantasy', icon: Sparkles, color: 'from-purple-600/30 to-violet-600/10 border-purple-500/30 text-purple-300' },
  { name: 'Drama', icon: Heart, color: 'from-blue-600/30 to-indigo-600/10 border-blue-500/30 text-blue-300' },
  { name: 'Mystery', icon: Eye, color: 'from-violet-600/30 to-fuchsia-600/10 border-violet-500/30 text-violet-300' },
  { name: 'Supernatural', icon: Zap, color: 'from-amber-600/30 to-yellow-600/10 border-amber-500/30 text-amber-300' },
  { name: 'Adventure', icon: Compass, color: 'from-teal-600/30 to-emerald-600/10 border-teal-500/30 text-teal-300' },
  { name: 'Thriller', icon: Shield, color: 'from-indigo-600/30 to-purple-600/10 border-indigo-500/30 text-indigo-300' },
];

export default function GenreQuickFilter() {
  const navigate = useNavigate();

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Explore by Genre
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Dive directly into specific anime themes and categories
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 sm:gap-4">
        {TOP_GENRES.map((genre) => {
          const Icon = genre.icon;
          return (
            <button
              key={genre.name}
              onClick={() => navigate(`/discover?genre=${encodeURIComponent(genre.name)}`)}
              className={`p-4 rounded-2xl bg-gradient-to-br ${genre.color} border hover:scale-[1.03] transition-all duration-200 text-left flex items-center gap-3.5 shadow-sm group`}
            >
              <div className="p-2.5 rounded-xl bg-dark-950/60 border border-white/10 group-hover:bg-dark-900 transition">
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <div className="font-semibold text-sm text-white group-hover:text-brand-200 transition">
                  {genre.name}
                </div>
                <div className="text-[11px] text-slate-400">Browse titles →</div>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
