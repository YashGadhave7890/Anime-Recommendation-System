import React, { useState } from 'react';
import { Sparkles, Check, ArrowRight, Compass } from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { useToast } from '../../context/ToastContext';
import { setUserPreferences } from '../../api/interactions';

const QUICK_GENRES = [
  'Action',
  'Psychological',
  'Sci-Fi',
  'Comedy',
  'Fantasy',
  'Drama',
  'Mystery',
  'Supernatural',
  'Thriller',
  'Slice of Life',
];

export default function ColdStartBanner({ onPreferencesSaved }) {
  const { preferences, refreshUserData } = useUser();
  const { showToast } = useToast();
  const [selectedGenres, setSelectedGenres] = useState(
    preferences?.preferred_genres || ['Psychological', 'Sci-Fi']
  );
  const [saving, setSaving] = useState(false);

  const toggleGenre = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const handleSave = async () => {
    if (selectedGenres.length === 0) {
      showToast('Please select at least 1 favorite genre', 'error');
      return;
    }

    try {
      setSaving(true);
      await setUserPreferences(selectedGenres, ['TV', 'Movie']);
      await refreshUserData();
      showToast('Genre preferences saved! Tier 1 Cold-Start recommendations active.');
      if (onPreferencesSaved) onPreferencesSaved();
    } catch (err) {
      showToast(err.message || 'Failed to save preferences', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-brand-950/60 via-dark-900 to-violet-950/40 border border-brand-500/30 shadow-xl space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-500/30">
            <Compass className="w-3.5 h-3.5 text-brand-400" />
            <span>Two-Tier Cold-Start Onboarding</span>
          </div>
          <h3 className="text-xl font-bold text-white">
            Personalize Your Feed in Seconds
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
            You are exploring with a fresh profile. Pick your favorite anime genres below so ANIMORA can activate Tier 1 genre-conditioned Bayesian rankings!
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="shrink-0 flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs sm:text-sm shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
        >
          <span>{saving ? 'Saving...' : 'Activate Recommendations'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Genre Picker Chips */}
      <div className="flex flex-wrap gap-2 pt-1">
        {QUICK_GENRES.map((genre) => {
          const isSelected = selectedGenres.includes(genre);
          return (
            <button
              key={genre}
              type="button"
              onClick={() => toggleGenre(genre)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                isSelected
                  ? 'bg-brand-600 text-white border border-brand-400/50 shadow-glow-sm'
                  : 'bg-dark-850 hover:bg-dark-800 text-slate-300 border border-slate-700/80 hover:text-white'
              }`}
            >
              <span>{genre}</span>
              {isSelected && <Check className="w-3.5 h-3.5" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
