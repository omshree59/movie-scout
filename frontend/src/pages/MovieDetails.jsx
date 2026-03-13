import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { movieAPI } from '../services/api';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import StarRating from '../components/StarRating';
import { motion } from 'framer-motion';
import { useApp } from '../store/AppContext';
import { Plus, Check, ChevronLeft, Calendar, Clock, Globe, LogIn } from 'lucide-react';

const LABELS = ['Terrible', 'Poor', 'Okay', 'Good', 'Amazing'];

const MovieDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isFavorite, toggleFavorite, user, setOnAuthRequired } = useApp();

  const [movie, setMovie]           = useState(null);
  const [similar, setSimilar]       = useState([]);
  const [userRating, setUserRating] = useState(0);
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [ratingLoading, setRatingLoading]     = useState(false);

  // Register auth redirect handler for this page
  useEffect(() => {
    setOnAuthRequired(() => () => navigate('/login'));
    return () => setOnAuthRequired(() => () => {});
  }, [navigate, setOnAuthRequired]);

  // Scroll to top whenever the movie changes (e.g. clicking "More Like This")
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [id]);

  // Fetch movie details
  useEffect(() => {
    const fetchMovie = async () => {
      // Reset stale state immediately so old movie doesn't linger
      setMovie(null);
      setSimilar([]);
      setUserRating(0);
      setRatingSubmitted(false);

      if (id === 'interstellar') {
        setMovie({
          movie_id: 'interstellar', title: 'Interstellar',
          description: "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
          year: 2014, runtime: '2h 49m', genres: 'Sci-Fi|Adventure|Drama',
          poster_url: `https://placehold.co/600x900/111/444?text=Interstellar`,
          cast: ['Matthew McConaughey', 'Anne Hathaway', 'Jessica Chastain'],
          rating: 4.8, vote_count: 12000,
        });
        return;
      }
      try {
        const { data } = await movieAPI.getMovieById(id);
        // Build a wide backdrop URL
        let backdropUrl = data.backdrop_url || '';
        if (!backdropUrl && data.poster_url) {
          backdropUrl = data.poster_url.replace('/w500/', '/w1280/');
        }
        setMovie({
          ...data,
          backdrop_url: backdropUrl || data.poster_url,
          description: data.description || `${data.title} — an incredible story you won't forget.`,
          runtime: data.runtime || '1h 50m – 2h 20m per ep.',
        });
      } catch (err) {
        console.error('Error fetching movie:', err);
      }
    };
    fetchMovie();
  }, [id]);

  // Fetch similar movies
  useEffect(() => {
    const fetchSimilar = async () => {
      try {
        const { data } = await movieAPI.getSimilar(id, 8);
        setSimilar(Array.isArray(data) ? data : (data.movies || []));
      } catch { /* silent */ }
    };
    if (id !== 'interstellar') fetchSimilar();
  }, [id]);

  const handleRate = async (rating) => {
    // Guard: must be signed in
    if (!user) {
      navigate('/login');
      return;
    }
    setUserRating(rating);
    setRatingLoading(true);
    try {
      await movieAPI.rateMovie(user.uid, Number(id), rating);
      setRatingSubmitted(true);
    } catch (err) {
      console.error('Rating error:', err);
    } finally {
      setRatingLoading(false);
    }
  };

  if (!movie) {
    return (
      <div className="bg-netflixDark min-h-screen flex items-center justify-center">
        <div className="w-14 h-14 border-4 border-netflixRed border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const genres = typeof movie.genres === 'string'
    ? movie.genres.split('|').filter(Boolean)
    : (movie.genres || []);

  const avgRating = movie.rating ? parseFloat(movie.rating) : null;

  return (
    <div className="bg-netflixDark min-h-screen text-white">
      <Navbar />

      {/* ── Hero Banner (80vh) ── */}
      <div className="relative w-full" style={{ minHeight: '80vh' }}>
        {/* Background poster */}
        <div className="absolute inset-0 overflow-hidden">
          <img
            src={movie.backdrop_url || movie.poster_url || `https://placehold.co/1920x1080/111/333?text=${encodeURIComponent(movie.title)}`}
            alt={movie.title}
            className="w-full h-full object-cover"
            style={{ objectPosition: 'center center' }}
          />
          {/* Gradient overlays: bottom + left + dark vignette */}
          <div className="absolute inset-0 bg-gradient-to-t from-netflixDark via-netflixDark/70 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-netflixDark via-netflixDark/50 to-transparent w-4/5" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex flex-col justify-end px-6 md:px-14" style={{ minHeight: '80vh', paddingBottom: '60px' }}>
          {/* Back button */}
          <motion.button
            onClick={() => navigate(-1)}
            className="absolute top-24 left-6 md:left-14 flex items-center gap-1 text-white/60 hover:text-white text-sm transition-colors"
            whileHover={{ x: -2 }}
          >
            <ChevronLeft size={18} /> Back
          </motion.button>

          {/* Title */}
          <motion.h1
            className="text-4xl md:text-6xl lg:text-7xl font-black text-white mb-4 leading-none drop-shadow-2xl"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {movie.title}
          </motion.h1>

          {/* Metadata badges */}
          <motion.div
            className="flex flex-wrap items-center gap-3 mb-6 text-sm font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            {movie.year && (
              <span className="flex items-center gap-1 text-white/70">
                <Calendar size={14} /> {movie.year}
              </span>
            )}
            {movie.runtime && (
              <span className="flex items-center gap-1 text-white/70">
                <Clock size={14} /> {movie.runtime}
              </span>
            )}
            <span className="border border-white/30 text-white/70 px-2 py-0.5 rounded text-xs">16+</span>
            <span className="flex items-center gap-1 text-white/70">
              <Globe size={14} /> Korean
            </span>
            {genres.slice(0, 2).map(g => (
              <span key={g} className="bg-white/10 backdrop-blur-sm text-white/80 px-2.5 py-0.5 rounded-full text-xs font-semibold">
                {g}
              </span>
            ))}
          </motion.div>

          {/* Description */}
          <motion.p
            className="text-white/90 text-base md:text-lg max-w-2xl leading-relaxed mb-8 drop-shadow-md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
          >
            {movie.description}
          </motion.p>

          {/* Action buttons */}
          <motion.div
            className="flex items-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
          >
            <button
              onClick={() => toggleFavorite(movie)}
              className="flex items-center gap-2 bg-netflixRed text-white px-8 py-3 rounded-md font-bold text-base hover:bg-red-700 transition shadow-xl"
            >
              {isFavorite(id) ? <Check size={20} /> : <Plus size={20} />}
              {isFavorite(id) ? 'In My List' : 'Add to My List'}
            </button>
          </motion.div>
        </div>
      </div>

      {/* ── Content Section Below Hero ── */}
      <div className="px-6 md:px-14 pb-24 -mt-2 relative z-10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-10">

          {/* LEFT: About + Rating */}
          <div className="lg:col-span-2 space-y-10">

            {/* About This Drama */}
            {movie.suitable_for && (
              <motion.section
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="text-2xl font-black mb-4 tracking-tight">Why Watch This?</h2>
                <div className="border-l-4 border-netflixRed pl-5 bg-white/[0.03] rounded-r-xl p-5">
                  <p className="text-white/80 leading-relaxed italic text-base">
                    "{movie.suitable_for}"
                  </p>
                </div>
              </motion.section>
            )}

            {/* Full Synopsis */}
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-black mb-4 tracking-tight">About This Drama</h2>
              <p className="text-white/70 leading-loose text-base">
                {movie.description}
              </p>
            </motion.section>

            {/* ── Star Rating System ── */}
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur-sm"
            >
              <h2 className="text-2xl font-black mb-1 tracking-tight">Rate This Drama</h2>
              <p className="text-white/40 text-sm mb-5">How would you rate your experience?</p>

              {ratingSubmitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col gap-3"
                >
                  <div className="flex items-center gap-3 text-yellow-400">
                    <StarRating value={userRating} readOnly size={32} />
                    <span className="font-bold text-xl">{LABELS[userRating - 1]}</span>
                  </div>
                  <p className="text-green-400 text-sm font-semibold">✓ Thanks for rating! Your feedback helps others discover great dramas.</p>
                </motion.div>
              ) : (
                <div className="flex flex-col gap-4">
                  <StarRating
                    value={userRating}
                    onChange={handleRate}
                    size={36}
                    avgRating={avgRating}
                    totalRatings={movie.vote_count}
                  />
                  {userRating > 0 && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-white/50 text-sm"
                    >
                      You selected: <span className="text-yellow-400 font-bold">{LABELS[userRating - 1]}</span>
                      {ratingLoading && ' — Saving...'}
                    </motion.p>
                  )}
                </div>
              )}

              {/* Average bar */}
              {avgRating && (
                <div className="mt-5 pt-4 border-t border-white/10">
                  <p className="text-white/40 text-xs uppercase tracking-widest mb-2">Community Rating</p>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-white/10 rounded-full h-2 overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${(avgRating / 5) * 100}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                    <span className="text-yellow-400 font-bold text-sm whitespace-nowrap">
                      {avgRating.toFixed(1)} / 5
                    </span>
                  </div>
                </div>
              )}
            </motion.section>
          </div>

          {/* RIGHT: Details sidebar */}
          <motion.aside
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
              <h3 className="text-lg font-bold mb-5 text-white/90">Details</h3>

              <dl className="space-y-5 text-sm">
                {movie.cast && movie.cast.length > 0 && (
                  <div>
                    <dt className="text-white/40 uppercase tracking-widest text-[10px] mb-1.5">Cast</dt>
                    <dd className="flex flex-wrap gap-2">
                      {movie.cast.map(actor => (
                        <span key={actor} className="bg-white/10 px-2.5 py-1 rounded-full text-white/80 text-xs font-medium">
                          {actor}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}

                {genres.length > 0 && (
                  <div>
                    <dt className="text-white/40 uppercase tracking-widest text-[10px] mb-1.5">Genres</dt>
                    <dd className="flex flex-wrap gap-2">
                      {genres.map(g => (
                        <span key={g} className="border border-netflixRed/60 text-netflixRed px-2.5 py-1 rounded-full text-xs font-semibold">
                          {g}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}

                {movie.year && (
                  <div>
                    <dt className="text-white/40 uppercase tracking-widest text-[10px] mb-1">Release Year</dt>
                    <dd className="text-white/80 font-medium">{movie.year}</dd>
                  </div>
                )}

                <div>
                  <dt className="text-white/40 uppercase tracking-widest text-[10px] mb-1">Language</dt>
                  <dd className="text-white/80 font-medium">Korean (with subtitles)</dd>
                </div>

                <div>
                  <dt className="text-white/40 uppercase tracking-widest text-[10px] mb-1">Duration</dt>
                  <dd className="text-white/80 font-medium">{movie.runtime || '~1h 10m per episode'}</dd>
                </div>
              </dl>
            </div>
          </motion.aside>
        </div>

        {/* ── More Like This ── */}
        {similar.length > 0 && (
          <motion.section
            className="mt-16"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-2xl font-black mb-6 tracking-tight">More Like This</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {similar.map((m, i) => {
                // Ensure every similar card has a usable movie_id for routing
                const cardMovie = {
                  ...m,
                  movie_id: m.movie_id ?? m.tmdb_id ?? m.id ?? i,
                };
                return (
                  <motion.div
                    key={cardMovie.movie_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 * i }}
                  >
                    <MovieCard movie={cardMovie} variant="grid" />
                  </motion.div>
                );
              })}
            </div>
          </motion.section>
        )}
      </div>
    </div>
  );
};

export default MovieDetails;
