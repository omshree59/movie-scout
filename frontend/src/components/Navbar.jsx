import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Home, LayoutDashboard, Clock, Menu, X, Heart, LogOut } from 'lucide-react';
import { useApp } from '../store/AppContext';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';
import { movieAPI } from '../services/api';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const [searchVal, setSearchVal] = useState('');
  const { user } = useApp();

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/login');
    } catch (error) {
      console.error("Error signing out: ", error);
    }
  };

  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (searchVal.trim().length === 0) {
        setSuggestions([]);
        return;
      }
      setIsSearching(true);
      try {
        const { data } = await movieAPI.search(searchVal, 'keyword', 8);
        setSuggestions(data.movies || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsSearching(false);
      }
    };

    const timer = setTimeout(() => {
      fetchSuggestions();
    }, 300);

    return () => clearTimeout(timer);
  }, [searchVal]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleSearchChange = (e) => {
    setSearchVal(e.target.value);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchVal.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchVal.trim())}`);
    } else {
      navigate('/search');
    }
  };

  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/search', label: 'Browse', icon: Search },
    { to: '/taste-profile', label: 'Taste Profile', icon: Heart },
    { to: '/dashboard', label: 'My List', icon: LayoutDashboard },
  ];

  return (
    <motion.nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-netflixDark/95 backdrop-blur-md shadow-2xl' : 'bg-gradient-to-b from-black/80 to-transparent'
      }`}
      initial={{ y: -60 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-full px-4 md:px-12 lg:px-16 transition-all duration-300">
        <div className="flex items-center h-16 transition-all">
          {/* Logo (Shifted left by removing max-w-7xl and increasing padding) */}
          <Link to="/" className="flex items-center space-x-2 mr-8 md:mr-12 hover:scale-105 transition-transform">
            <span className="text-netflixRed font-black text-3xl tracking-tighter drop-shadow-md">MOVIE</span>
            <span className="text-white font-black text-3xl tracking-tighter drop-shadow-md">SCOUT</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-7 flex-1">
            {navLinks.map(({ to, label }) => {
              const isActive = location.pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  className={`relative text-sm transition-all duration-300 ${
                    isActive 
                      ? 'text-white font-bold drop-shadow-lg scale-105' 
                      : 'text-white/70 font-medium hover:text-white hover:drop-shadow-md'
                  }`}
                >
                  {label}
                  {isActive && (
                    <motion.div 
                      layoutId="nav-indicator"
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-netflixRed rounded-full shadow-[0_0_8px_rgba(229,9,20,0.8)]"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center justify-end">
            <div className="relative hidden md:block z-50">
              <form 
                onSubmit={handleSearch} 
                className={`flex items-center rounded-full px-4 py-1.5 gap-2 transition-all duration-300 ${
                  showSuggestions || searchVal 
                    ? 'bg-black/80 border border-white/30 shadow-[0_0_15px_rgba(255,255,255,0.1)]' 
                    : 'bg-black/40 border border-white/10 hover:border-white/40'
                }`}
              >
                <Search size={16} className={showSuggestions || searchVal ? 'text-white' : 'text-white/60'} />
                <input
                  type="text"
                  value={searchVal}
                  onChange={handleSearchChange}
                  onFocus={() => setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                  placeholder="Search titles, genres, cast..."
                  className="bg-transparent text-sm text-white placeholder-white/40 outline-none w-48 lg:w-64 transition-all"
                />
              </form>

              {/* Suggestions Dropdown */}
              <AnimatePresence>
                {showSuggestions && searchVal.trim().length > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
                    animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full mt-3 w-full min-w-[320px] right-0 bg-[#141414]/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-[0_20px_40px_rgba(0,0,0,0.8)] overflow-hidden"
                  >
                    {isSearching && suggestions.length === 0 ? (
                      <div className="p-4 text-sm text-netflixGray text-center">Searching...</div>
                    ) : suggestions.length > 0 ? (
                      <div className="max-h-[70vh] overflow-y-auto">
                        {suggestions.map((movie) => (
                          <div 
                            key={movie.movie_id}
                            onMouseDown={() => {
                              navigate(`/movie/${movie.movie_id}`);
                              setShowSuggestions(false);
                              setSearchVal('');
                            }}
                            className="flex items-center gap-3 p-3 hover:bg-[#2a2a2a] cursor-pointer transition-colors border-b border-white/5 last:border-0"
                          >
                            <img 
                              src={movie.poster_url || `https://placehold.co/40x60/222222/FFF?text=${encodeURIComponent(movie.title.charAt(0))}`} 
                              alt={movie.title}
                              className="w-10 h-14 object-cover rounded-sm"
                            />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-bold text-white truncate">{movie.title}</p>
                              <div className="flex items-center gap-2 mt-0.5">
                                {movie.score && <p className="text-xs text-green-500 font-bold">{movie.score}% Match</p>}
                                <p className="text-xs text-netflixGray truncate">{movie.genres}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-sm text-netflixGray text-center">No results for "{searchVal}"</div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="hidden md:flex items-center space-x-4 ml-4 border-l border-white/10 pl-6">
              {user ? (
                <div className="flex items-center space-x-4">
                  <div className="w-8 h-8 rounded bg-netflixRed flex items-center justify-center font-bold text-sm shadow-[0_0_10px_rgba(229,9,20,0.5)] cursor-pointer hover:scale-105 transition-transform">
                    {user.email?.charAt(0).toUpperCase()}
                  </div>
                  <button onClick={handleLogout} className="text-white/60 hover:text-white transition-colors">
                    <LogOut size={18} />
                  </button>
                </div>
              ) : (
                <Link to="/login" className="bg-netflixRed text-white px-5 py-1.5 rounded font-bold text-sm hover:bg-[#c11119] transition-all hover:shadow-[0_0_15px_rgba(229,9,20,0.4)]">
                  Sign In
                </Link>
              )}
            </div>
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden text-white p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="md:hidden bg-netflixDark/98 border-t border-white/10 px-4 py-4"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {navLinks.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 py-3 text-netflixLightGray hover:text-white"
              >
                <Icon size={18} /> {label}
              </Link>
            ))}
            <form onSubmit={handleSearch} className="flex items-center bg-white/10 rounded-xl px-3 py-2 mt-3 gap-2">
              <Search size={14} className="text-netflixGray" />
              <input
                type="text"
                value={searchVal}
                onChange={handleSearchChange}
                placeholder="Search movies..."
                className="bg-transparent text-sm text-white placeholder-netflixGray outline-none flex-1"
              />
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default Navbar;
