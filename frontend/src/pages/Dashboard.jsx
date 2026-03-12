import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useApp } from '../store/AppContext';

const Dashboard = () => {
  const { favorites, watchHistory } = useApp();
  const navigate = useNavigate();

  return (
    <div className="bg-netflixDark min-h-screen text-white pb-20 pt-24">
      <Navbar />
      <div className="px-4 md:px-8 max-w-7xl mx-auto space-y-12">
        <section>
          <h2 className="text-2xl font-bold mb-6 text-netflixLightGray border-b border-white/10 pb-2">My List</h2>
          {favorites.length === 0 ? (
            <p className="text-netflixGray">You haven't added any movies to your list yet.</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {favorites.map(movie => (
                <div key={movie.movie_id} onClick={() => navigate(`/movie/${movie.movie_id}`)} className="w-full relative group cursor-pointer hover:scale-105 transition-transform overflow-hidden rounded-md shadow-lg border border-white/10 bg-[#141414]">
                  <div className="h-[225px] md:h-[300px] overflow-hidden rounded-t-md relative">
                    <img 
                      src={movie.poster_url || movie.poster || `https://placehold.co/300x450/222222/FFF?text=${encodeURIComponent(movie.title)}`} 
                      alt={movie.title} 
                      className="w-full h-full object-cover transition duration-300 group-hover:scale-110"
                    />
                    <div className="absolute inset-0 flex items-center justify-center p-4 -z-10 bg-black/50">
                      <span className="text-white/50 text-center text-sm font-bold">{movie.title}</span>
                    </div>
                  </div>
                  <div className="p-3 bg-[#181818] rounded-b-md h-20">
                    <h3 className="text-white font-bold text-sm truncate" title={movie.title}>
                      {movie.title}
                    </h3>
                    {movie.cast && movie.cast.length > 0 ? (
                      <p className="text-netflixGray text-xs mt-1 line-clamp-2 leading-tight" title={movie.cast.join(", ")}>
                        {movie.cast.join(", ")}
                      </p>
                    ) : (
                      <span className="text-netflixRed text-xs font-bold mt-1 block">My List</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-6 text-netflixLightGray border-b border-white/10 pb-2">Watch History</h2>
          {watchHistory.length === 0 ? (
            <p className="text-netflixGray">Your watch history is empty.</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {watchHistory.map(movie => (
                <div key={movie.movie_id} onClick={() => navigate(`/movie/${movie.movie_id}`)} className="w-full relative group cursor-pointer hover:scale-105 transition-transform overflow-hidden rounded-md shadow-lg border border-white/10 bg-[#141414] opacity-80 hover:opacity-100">
                  <div className="h-[225px] md:h-[300px] overflow-hidden rounded-t-md relative">
                    <img 
                      src={movie.poster_url || movie.poster || `https://placehold.co/300x450/222222/FFF?text=${encodeURIComponent(movie.title)}`} 
                      alt={movie.title} 
                      className="w-full h-full object-cover transition duration-300 group-hover:scale-110"
                    />
                    <div className="absolute inset-0 flex items-center justify-center p-4 -z-10 bg-black/50">
                      <span className="text-white/50 text-center text-sm font-bold">{movie.title}</span>
                    </div>
                  </div>
                  <div className="p-3 bg-[#181818] rounded-b-md h-20">
                    <h3 className="text-white font-bold text-sm truncate" title={movie.title}>
                      {movie.title}
                    </h3>
                    {movie.cast && movie.cast.length > 0 ? (
                      <p className="text-netflixGray text-xs mt-1 line-clamp-2 leading-tight" title={movie.cast.join(", ")}>
                        {movie.cast.join(", ")}
                      </p>
                    ) : (
                      <span className="text-netflixGray text-xs font-bold mt-1 block">Watched</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
