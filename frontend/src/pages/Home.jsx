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
    <div className="relative h-[80vh] w-full mt-0">
      <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-netflixDark to-transparent z-10"></div>
      <img
        src="https://raw.githubusercontent.com/omshree59/movie-assets/main/posters/cloy.jpg"
        alt="Hero Background"
        className="w-full h-full object-cover"
      />
      <div className="absolute top-[30%] left-[5%] z-20 max-w-2xl">
        <motion.h1 
          className="text-5xl md:text-7xl font-black text-white mb-4 drop-shadow-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          CRASH LANDING ON YOU
        </motion.h1>
        <motion.p 
          className="text-lg md:text-xl text-white/90 mb-6 drop-shadow-md font-medium"
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
            onClick={() => navigate('/movie/15')}
            className="bg-netflixRed text-white px-8 py-3 rounded-md font-bold text-lg hover:bg-[#c11119] transition shadow-lg">
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
