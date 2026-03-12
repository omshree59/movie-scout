import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * StarRating component
 * Props:
 *   value       — current selected rating (1-5), 0 = none
 *   onChange    — (rating: number) => void  called when user clicks a star
 *   readOnly    — if true, no hover/click effects
 *   size        — pixel size of each star (default 28)
 *   avgRating   — optional average rating to display beneath stars
 *   totalRatings — optional count of raters
 */
const StarRating = ({ value = 0, onChange, readOnly = false, size = 28, avgRating, totalRatings }) => {
  const [hovered, setHovered] = useState(0);

  const activeStar = hovered || value;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map(star => {
          const filled = star <= activeStar;
          return (
            <motion.button
              key={star}
              type="button"
              disabled={readOnly}
              onClick={() => !readOnly && onChange?.(star)}
              onMouseEnter={() => !readOnly && setHovered(star)}
              onMouseLeave={() => !readOnly && setHovered(0)}
              whileHover={!readOnly ? { scale: 1.3, y: -2 } : {}}
              whileTap={!readOnly ? { scale: 0.9 } : {}}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className={`relative cursor-${readOnly ? 'default' : 'pointer'} focus:outline-none`}
              aria-label={`Rate ${star} star${star !== 1 ? 's' : ''}`}
            >
              <Star
                size={size}
                className={`transition-colors duration-150 ${
                  filled
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-white/25 fill-transparent'
                }`}
              />
            </motion.button>
          );
        })}

        {/* Show selected rating number */}
        <AnimatePresence mode="wait">
          {!readOnly && value > 0 && (
            <motion.span
              key={value}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              className="ml-2 text-yellow-400 font-bold text-sm"
            >
              {value}/5
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Average rating display */}
      {avgRating != null && (
        <p className="text-white/50 text-xs">
          <span className="text-yellow-400 font-semibold">{avgRating.toFixed(1)}</span>
          &nbsp;/ 5 avg
          {totalRatings != null && ` · ${totalRatings.toLocaleString()} ratings`}
        </p>
      )}
    </div>
  );
};

export default StarRating;
