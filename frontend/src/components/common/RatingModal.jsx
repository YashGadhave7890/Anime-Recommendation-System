import React, { useState, useEffect } from 'react';
import { X, Star, Send } from 'lucide-react';
import StarRating from './StarRating';
import { submitRating } from '../../api/interactions';
import { useUser } from '../../context/UserContext';
import { useToast } from '../../context/ToastContext';

export default function RatingModal({ isOpen, onClose, animeId, animeTitle, initialRating = 0, initialReview = '' }) {
  const { refreshUserData } = useUser();
  const { showToast } = useToast();
  const [rating, setRating] = useState(initialRating || 8);
  const [review, setReview] = useState(initialReview || '');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialRating) setRating(initialRating);
    if (initialReview) setReview(initialReview);
  }, [initialRating, initialReview, isOpen]);

  // Keyboard accessibility: Close dialog on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rating || rating < 1) {
      showToast('Please select a rating between 1 and 10', 'error');
      return;
    }

    try {
      setSubmitting(true);
      await submitRating(animeId, rating, review);
      await refreshUserData();
      showToast(`Rated "${animeTitle}" ${rating}/10! Personalized recommendations updated.`);
      onClose();
    } catch (err) {
      showToast(err.message || 'Failed to submit rating', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="rating-modal-title"
    >
      <div className="relative w-full max-w-lg rounded-3xl bg-dark-900 border border-slate-700/80 shadow-2xl p-6 sm:p-8">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-2">
            <Star className="w-3.5 h-3.5 fill-amber-400" />
            <span>Community & ML Feedback</span>
          </div>
          <h3 id="rating-modal-title" className="text-xl font-bold text-slate-100">Rate this Anime</h3>
          <p className="text-slate-400 text-sm line-clamp-1 mt-1 font-medium">{animeTitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Star selector */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-slate-800 flex flex-col items-center justify-center space-y-3">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">
              Your Score (1 to 10)
            </span>
            <StarRating rating={rating} onChange={setRating} size="lg" />
            <span className="text-xs text-brand-300 font-medium">
              {rating >= 8
                ? 'Masterpiece / Greatly Enjoyed'
                : rating >= 6
                ? 'Good / Enjoyable'
                : rating >= 4
                ? 'Average / Mediocre'
                : 'Disliked'}
            </span>
          </div>

          {/* Optional Review */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Review & Notes (Optional)
            </label>
            <textarea
              value={review}
              onChange={(e) => setReview(e.target.value)}
              placeholder="What made this anime stand out to you? Write your thoughts..."
              rows={3}
              maxLength={1000}
              className="w-full px-4 py-3 rounded-2xl bg-dark-850 border border-slate-700/80 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-sm resize-none transition"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 text-sm font-medium transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold shadow-glow-sm hover:shadow-glow-md transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{submitting ? 'Submitting...' : 'Save Rating'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
