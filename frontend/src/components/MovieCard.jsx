import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Star, Plus } from 'lucide-react';

/**
 * MovieCard — A Netflix-style responsive poster card.
 * Uses a fixed 2:3 aspect ratio with object-cover so every
 * poster looks perfect regardless of source dimensions.
 *
 * Props:
 *   movie      — { movie_id, title, poster_url, genres, cast, rating, score }
 *   variant    — "row" (default, fixed-width for scroll rows) | "grid" (fills grid column)
 *   onClick    — optional override for click behaviour
 */
const MovieCard = ({ movie, variant = 'row', onClick }) => {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  const handleClick = onClick || (() => navigate(`/movie/${movie.movie_id}`));

  const posterUrl = (!imgError && movie.poster_url)
    ? movie.poster_url
    : `https://placehold.co/300x450/141414/888888?text=${encodeURIComponent(movie.title || 'Movie')}`;

  const matchPct = movie.score
    ? `${Math.round(movie.score)}% Match`
    : '98% Match';

  // Width class — scrollable row uses fixed width, grid fills column
  const wrapClass = variant === 'grid'
    ? 'w-full cursor-pointer group'
    : 'flex-none w-[150px] md:w-[195px] cursor-pointer group';

  return (
    <motion.div
      className={wrapClass}
      onClick={handleClick}
      whileHover={{ scale: 1.05, y: -4, zIndex: 20 }}
      transition={{ type: 'spring', stiffness: 380, damping: 28 }}
    >
      {/* ── Poster container: fixed 2:3 ratio, overflow hidden ── */}
      <div
        style={{ aspectRatio: '2 / 3' }}
        className="relative w-full overflow-hidden rounded-xl bg-[#141414] shadow-lg border border-white/[0.06]"
      >
        <img
          src={posterUrl}
          alt={movie.title}
          onError={() => setImgError(true)}
          className="w-full h-full object-cover block transition-transform duration-500 group-hover:scale-110"
          draggable={false}
        />

        {/* Dark gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />

        {/* Info that slides up on hover */}
        <div className="absolute bottom-0 left-0 right-0 p-3 translate-y-3 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
          <p className="text-white font-bold text-sm leading-snug line-clamp-2 drop-shadow-md">
            {movie.title}
          </p>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-green-400 text-xs font-semibold">{matchPct}</span>
            {movie.genres && (
              <span className="text-white/50 text-xs truncate">
                {typeof movie.genres === 'string'
                  ? movie.genres.split('|')[0]
                  : movie.genres[0]}
              </span>
            )}
          </div>
        </div>

        {/* Rating badge (top-right) */}
        {movie.rating && (
          <div className="absolute top-2 right-2 flex items-center gap-1 bg-black/60 backdrop-blur-sm rounded-full px-2 py-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <Star size={10} className="text-yellow-400 fill-yellow-400" />
            <span className="text-white text-[10px] font-bold">
              {typeof movie.rating === 'number' ? movie.rating.toFixed(1) : movie.rating}
            </span>
          </div>
        )}
      </div>

      {/* Title + cast below poster */}
      <div className="pt-2 px-0.5">
        <h3 className="text-white text-xs font-semibold truncate leading-tight" title={movie.title}>
          {movie.title}
        </h3>
        {movie.cast && movie.cast.length > 0 && (
          <p className="text-white/40 text-[10px] mt-0.5 truncate leading-tight" title={movie.cast.join(', ')}>
            {movie.cast.slice(0, 2).join(', ')}
          </p>
        )}
      </div>
    </motion.div>
  );
};

export default MovieCard;
