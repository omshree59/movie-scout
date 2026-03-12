import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { movieAPI } from '../services/api';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import { motion } from 'framer-motion';

const Search = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      try {
        if (!query) {
          // When browse is clicked or query is empty, show a mix (simulate an explore page)
          const { data } = await movieAPI.getTrending(30);
          setResults(data.movies || data || []);
        } else {
          const { data } = await movieAPI.search(query, 'keyword', 30);
          setResults(data.movies || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [query]);

  return (
    <div className="bg-netflixDark min-h-screen text-white pb-20 pt-24">
      <Navbar />
      <div className="px-4 md:px-8 max-w-7xl mx-auto">
        <h1 className="text-2xl md:text-3xl font-bold mb-8 text-netflixLightGray">
          {query ? `Search Results for "${query}"` : 'Explore Movies'}
        </h1>
        
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-12 h-12 border-4 border-netflixRed border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : results.length === 0 && query ? (
          <div className="flex flex-col items-center justify-center py-20 text-netflixGray">
            <p className="text-xl">No results for "{query}"</p>
            <p className="mt-2 text-sm">Suggestions: Try different keywords or check spelling.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 border-t border-white/10 pt-8">
            {results.map(movie => (
              <MovieCard key={movie.movie_id} movie={movie} variant="grid" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;
