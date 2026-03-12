import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import { movieAPI } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft } from 'lucide-react';

// Map URL slug → display name + emoji
const GENRE_META = {
  romance:   { label: 'Romance & Love',    emoji: '💕', color: 'from-pink-600 to-rose-800' },
  happy:     { label: 'Laugh Out Loud',    emoji: '😂', color: 'from-yellow-500 to-orange-600' },
  action:    { label: 'Action & Thrills',  emoji: '⚔️', color: 'from-red-600 to-red-900' },
  drama:     { label: 'Deep Drama',        emoji: '🎭', color: 'from-purple-600 to-indigo-900' },
  sad:       { label: 'Heartbreak',        emoji: '💔', color: 'from-indigo-600 to-violet-900' },
  healing:   { label: 'Healing & Feel-Good', emoji: '🌿', color: 'from-emerald-500 to-teal-700' },
  thriller:  { label: 'Thriller & Suspense', emoji: '🔪', color: 'from-slate-700 to-gray-900' },
  adventure: { label: 'Sci-Fi & Fantasy',  emoji: '🚀', color: 'from-blue-500 to-cyan-700' },
  horror:    { label: 'Spooky & Horror',   emoji: '👻', color: 'from-gray-700 to-black' },
};

const GenrePage = () => {
  const { mood } = useParams();
  const navigate = useNavigate();
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  const meta = GENRE_META[mood] || { label: mood, emoji: '🎬', color: 'from-gray-700 to-gray-900' };

  useEffect(() => {
    const fetchGenreMovies = async () => {
      setLoading(true);
      try {
        const { data } = await movieAPI.getMoodRecs(mood, 15);
        // API returns array directly for mood endpoint
        setMovies(Array.isArray(data) ? data : (data.movies || []));
      } catch (err) {
        console.error('Failed to fetch genre movies:', err);
        setMovies([]);
      } finally {
        setLoading(false);
      }
    };
    fetchGenreMovies();
  }, [mood]);

  return (
    <div className="bg-netflixDark min-h-screen text-white pb-20">
      <Navbar />

      {/* Hero Banner */}
      <div className={`relative h-52 md:h-64 w-full bg-gradient-to-br ${meta.color} flex items-end overflow-hidden`}>
        {/* Animated background glow */}
        <div className="absolute inset-0 bg-black/30" />
        <div className="absolute -top-10 -right-10 w-72 h-72 rounded-full bg-white/5 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-netflixDark to-transparent" />

        <motion.div
          className="relative z-10 px-6 md:px-12 pb-6 md:pb-10"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Back button */}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1 text-white/60 hover:text-white text-sm mb-3 transition-colors"
          >
            <ChevronLeft size={16} /> Back
          </button>

          <div className="flex items-center gap-4">
            <span className="text-5xl md:text-6xl filter drop-shadow-lg">{meta.emoji}</span>
            <div>
              <p className="text-white/60 text-sm font-medium uppercase tracking-widest mb-1">KDramas for your mood</p>
              <h1 className="text-3xl md:text-5xl font-black text-white drop-shadow-md">{meta.label}</h1>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Movie Grid */}
      <div className="px-6 md:px-12 pt-8">
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="w-12 h-12 border-4 border-netflixRed border-t-transparent rounded-full animate-spin" />
          </div>
        ) : movies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-white/40">
            <span className="text-6xl mb-4">🎬</span>
            <p className="text-xl font-semibold">No movies found for this mood.</p>
            <button
              onClick={() => navigate('/taste-profile')}
              className="mt-6 px-6 py-3 bg-netflixRed text-white rounded-md font-bold hover:bg-red-700 transition"
            >
              Try another mood
            </button>
          </div>
        ) : (
          <AnimatePresence>
            <motion.div
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, staggerChildren: 0.05 }}
            >
              {movies.map((movie, i) => (
                <motion.div
                  key={movie.movie_id || i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                >
                  <MovieCard movie={movie} variant="grid" />
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};

export default GenrePage;
