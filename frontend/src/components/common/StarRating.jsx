import React, { useState } from 'react';
import { Star } from 'lucide-react';

export default function StarRating({ rating = 0, max = 10, onChange = null, readonly = false, size = 'md' }) {
  const [hoverRating, setHoverRating] = useState(0);

  const starSizes = {
    sm: 'w-3.5 h-3.5',
    md: 'w-5 h-5',
    lg: 'w-7 h-7',
  };

  const starSizeClass = starSizes[size] || starSizes.md;

  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: max }, (_, index) => {
        const starValue = index + 1;
        const isFilled = hoverRating ? starValue <= hoverRating : starValue <= Math.round(rating);

        return (
          <button
            key={starValue}
            type="button"
            disabled={readonly}
            onClick={() => !readonly && onChange && onChange(starValue)}
            onMouseEnter={() => !readonly && setHoverRating(starValue)}
            onMouseLeave={() => !readonly && setHoverRating(0)}
            className={`transition-transform duration-100 ${
              !readonly ? 'hover:scale-125 cursor-pointer' : 'cursor-default'
            }`}
            aria-label={`Rate ${starValue} of ${max}`}
          >
            <Star
              className={`${starSizeClass} ${
                isFilled
                  ? 'fill-amber-400 text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.5)]'
                  : 'text-slate-600 fill-slate-800/40'
              } transition-colors`}
            />
          </button>
        );
      })}
      <span className="ml-2 font-semibold text-slate-200 text-sm">
        {hoverRating ? hoverRating.toFixed(1) : rating ? Number(rating).toFixed(1) : '—'}
        <span className="text-slate-500 text-xs font-normal"> / {max}</span>
      </span>
    </div>
  );
}
