import React from 'react';
import { Film, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function EmptyState({
  title = 'No anime found',
  description = 'Try adjusting your search query or filters to discover more titles.',
  actionLabel = 'Discover Anime',
  actionTo = '/discover',
  icon: Icon = Film,
}) {
  return (
    <div className="w-full py-16 px-4 flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-center mb-4 text-slate-400">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-xl font-semibold text-slate-100 mb-2">{title}</h3>
      <p className="text-slate-400 max-w-md text-sm mb-6">{description}</p>
      {actionLabel && actionTo && (
        <Link
          to={actionTo}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition-all shadow-glow-sm hover:shadow-glow-md"
        >
          <span>{actionLabel}</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      )}
    </div>
  );
}
