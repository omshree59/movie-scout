import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { movieAPI } from '../services/api';
import { useApp } from '../store/AppContext';

const Hero = () => {
  const navigate = useNavigate();
  return (
    <div className="relative h-[80vh] w-full mt-0 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-t from-netflixDark via-netflixDark/50 to-transparent z-10 w-full h-full pointer-events-none"></div>
      
      {/* Subtle vignette on the sides to make it feel more cinematic */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-transparent z-10 w-full h-full pointer-events-none"></div>
      
      <img
        src="https://image.tmdb.org/t/p/original/o3Htmlg6BfNs8Ew7yjsRzVnYSEs.jpg"
        alt="Hero Background"
        className="w-full h-full object-cover object-[center_20%]"
      />
      
      <div className="absolute bottom-[20%] left-4 md:left-12 lg:left-16 z-20 max-w-2xl xl:max-w-3xl">
        <motion.h1 
          className="text-5xl md:text-7xl lg:text-8xl font-black text-white mb-2 md:mb-4 drop-shadow-[0_4px_10px_rgba(0,0,0,0.8)] tracking-tight leading-none"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          CRASH LANDING<br/>ON YOU
        </motion.h1>
        <motion.p 
          className="text-base md:text-xl lg:text-2xl text-white/90 mb-6 md:mb-8 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] font-medium max-w-xl leading-snug"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          A South Korean heiress paraglides into North Korea and into the life of an army officer, who decides he will help her hide.
        </motion.p>
        <motion.div 
          className="flex space-x-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <button 
            onClick={() => navigate('/movie/1')}
            className="flex items-center gap-2 bg-white text-black px-6 py-2.5 md:px-8 md:py-3.5 rounded-md font-bold text-base md:text-lg hover:bg-white/80 transition shadow-[0_4px_15px_rgba(255,255,255,0.3)] hover:scale-105">
            More Info
          </button>
        </motion.div>
      </div>
    </div>
  );
};

const MovieRow = ({ title, fetchFn }) => {
  const navigate = useNavigate();
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const rowRef = React.useRef(null);

  const scroll = (direction) => {
    if (rowRef.current) {
      const { scrollLeft, clientWidth } = rowRef.current;
      const scrollTo = direction === 'left' ? scrollLeft - clientWidth : scrollLeft + clientWidth;
      rowRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const getMovies = async () => {
      try {
        const { data } = await fetchFn();
        setMovies(data.movies || data);
      } catch (err) {
        console.error("Failed to fetch movies", err);
      } finally {
        setLoading(false);
      }
    };
    getMovies();
  }, [fetchFn]);

  if (loading) return <div className="py-6 px-4 md:px-8 text-netflixGray">Loading {title}...</div>;
  if (!movies || movies.length === 0) return null;

  return (
    <div className="py-6 px-4 md:px-8 relative z-20 group/row">
      <h2 className="text-xl md:text-2xl font-bold text-white mb-4">{title}</h2>
      
      <button 
        onClick={() => scroll('left')} 
        className="absolute left-0 top-[50%] z-40 bg-black/50 hover:bg-black/80 text-white h-[225px] md:h-[300px] w-12 flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
      >
        <ChevronLeft size={36} />
      </button>

      <div ref={rowRef} className="flex gap-3 overflow-x-auto hide-scrollbar pb-4 -mx-4 px-4 md:-mx-8 md:px-8 scroll-smooth">
        {movies.map(movie => (
          <MovieCard key={movie.movie_id || movie.id} movie={movie} variant="row" />
        ))}
      </div>
      
      <button 
        onClick={() => scroll('right')} 
        className="absolute right-0 top-[50%] z-40 bg-black/50 hover:bg-black/80 text-white h-[225px] md:h-[300px] w-12 flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
      >
        <ChevronRight size={36} />
      </button>
    </div>
  );
};

const Home = () => {
  const { userId, currentMood } = useApp();
  
  return (
    <div className="bg-netflixDark min-h-screen text-white pb-20">
      <Navbar />
      <Hero />
      <div className="-mt-32 relative z-20">
        <MovieRow title="Trending Now" fetchFn={() => movieAPI.getTrending(15)} />
        <MovieRow 
          title={currentMood ? `Based on Your Mood: ${currentMood}` : "Top Picks for You"} 
          fetchFn={() => currentMood ? movieAPI.getMoodRecs(currentMood, 15) : movieAPI.getRecommendations(userId, null, 'hybrid', 15)} 
        />
        <MovieRow title="💕 Romantic KDramas" fetchFn={() => movieAPI.getMoodRecs('romance', 15)} />
        <MovieRow title="😂 Comedies" fetchFn={() => movieAPI.getMoodRecs('happy', 15)} />
        <MovieRow title="💔 Heartbreak & Drama" fetchFn={() => movieAPI.getMoodRecs('sad', 15)} />
        <MovieRow title="⚔️ Action & Adventure" fetchFn={() => movieAPI.getMoodRecs('action', 15)} />
        <MovieRow title="🌿 Healing & Feel-Good" fetchFn={() => movieAPI.getMoodRecs('healing', 15)} />
        <MovieRow title="🔪 Thriller & Suspense" fetchFn={() => movieAPI.getMoodRecs('thriller', 15)} />
        <MovieRow title="🚀 Sci-Fi & Fantasy" fetchFn={() => movieAPI.getMoodRecs('adventure', 15)} />
      </div>
    </div>
  );
};

export default Home;
