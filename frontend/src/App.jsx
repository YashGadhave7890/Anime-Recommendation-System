import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import ScrollToTop from './components/common/ScrollToTop';
import EmptyState from './components/common/EmptyState';
import { Sparkles, Loader2 } from 'lucide-react';

// Lazy-loaded route components for optimal bundle splitting & performance
const HomePage = lazy(() => import('./pages/HomePage'));
const DiscoverPage = lazy(() => import('./pages/DiscoverPage'));
const AnimeDetailPage = lazy(() => import('./pages/AnimeDetailPage'));
const RecommendationsPage = lazy(() => import('./pages/RecommendationsPage'));
const WatchlistPage = lazy(() => import('./pages/WatchlistPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));

function PageLoader() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4 py-16 animate-fade-in" role="status" aria-label="Loading page content">
      <div className="relative w-12 h-12 flex items-center justify-center">
        <div className="absolute inset-0 rounded-2xl bg-brand-500/20 blur-lg animate-pulse" />
        <div className="w-10 h-10 rounded-xl bg-dark-900 border border-brand-500/40 flex items-center justify-center text-brand-400">
          <Loader2 className="w-5 h-5 animate-spin text-brand-400" />
        </div>
      </div>
      <p className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Loading ANIMORA...</p>
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100 selection:bg-brand-500/30 selection:text-brand-200">
      <ScrollToTop />
      <Navbar />

      <main className="flex-1" id="main-content">
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/discover" element={<DiscoverPage />} />
            <Route path="/anime/:id" element={<AnimeDetailPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            {/* Catch-all 404 Route */}
            <Route
              path="*"
              element={
                <div className="py-24 max-w-xl mx-auto px-4">
                  <EmptyState
                    title="Page Not Found"
                    description="The page you're looking for doesn't exist or has moved."
                    actionLabel="Return Home"
                    actionTo="/"
                  />
                </div>
              }
            />
          </Routes>
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
