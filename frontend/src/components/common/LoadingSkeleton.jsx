import React from 'react';

export function AnimeCardSkeleton() {
  return (
    <div className="rounded-2xl bg-dark-900 border border-slate-800/80 overflow-hidden flex flex-col animate-shimmer">
      <div className="aspect-[3/4] bg-slate-800/50 w-full" />
      <div className="p-3.5 space-y-2 flex-1 flex flex-col justify-between">
        <div className="space-y-1.5">
          <div className="h-4 bg-slate-800/70 rounded w-4/5" />
          <div className="h-3 bg-slate-800/50 rounded w-1/2" />
        </div>
        <div className="flex justify-between items-center pt-2">
          <div className="h-4 bg-slate-800/60 rounded w-12" />
          <div className="h-4 bg-slate-800/60 rounded w-10" />
        </div>
      </div>
    </div>
  );
}

export function AnimeGridSkeleton({ count = 12 }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <AnimeCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function HeroBannerSkeleton() {
  return (
    <div className="w-full h-[450px] md:h-[550px] rounded-3xl bg-dark-900 border border-slate-800/60 overflow-hidden animate-shimmer p-8 md:p-12 flex flex-col justify-end">
      <div className="max-w-2xl space-y-4">
        <div className="h-6 bg-slate-800/60 rounded w-32" />
        <div className="h-10 md:h-14 bg-slate-800/80 rounded w-4/5" />
        <div className="h-4 bg-slate-800/50 rounded w-full" />
        <div className="h-4 bg-slate-800/50 rounded w-3/4" />
        <div className="flex gap-4 pt-4">
          <div className="h-11 bg-slate-800/80 rounded-xl w-36" />
          <div className="h-11 bg-slate-800/50 rounded-xl w-36" />
        </div>
      </div>
    </div>
  );
}

export function DetailPageSkeleton() {
  return (
    <div className="space-y-8 animate-shimmer">
      <div className="h-96 rounded-3xl bg-dark-900 border border-slate-800/60 p-8 flex flex-col md:flex-row gap-8">
        <div className="w-64 h-80 bg-slate-800/80 rounded-2xl shrink-0" />
        <div className="flex-1 space-y-4">
          <div className="h-8 bg-slate-800/80 rounded w-3/4" />
          <div className="h-4 bg-slate-800/50 rounded w-1/3" />
          <div className="h-6 bg-slate-800/60 rounded w-1/2" />
          <div className="h-24 bg-slate-800/40 rounded-xl" />
        </div>
      </div>
    </div>
  );
}

export default AnimeCardSkeleton;
