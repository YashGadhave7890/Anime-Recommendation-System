import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorState({
  title = 'Failed to load content',
  message = 'We encountered an issue communicating with the ANIMORA backend. Please verify the server is running.',
  onRetry = null,
}) {
  return (
    <div className="w-full py-12 px-4 flex flex-col items-center justify-center text-center">
      <div className="w-14 h-14 rounded-2xl bg-rose-950/40 border border-rose-800/40 flex items-center justify-center mb-4 text-rose-400">
        <AlertTriangle className="w-7 h-7" />
      </div>
      <h3 className="text-lg font-semibold text-slate-100 mb-2">{title}</h3>
      <p className="text-slate-400 max-w-md text-sm mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
}
