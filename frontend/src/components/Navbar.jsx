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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-netflixRed font-black text-2xl tracking-tight">MOVIE</span>
            <span className="text-white font-black text-2xl tracking-tight">SCOUT</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-white ${
                  location.pathname === to ? 'text-white' : 'text-netflixLightGray'
                }`}
              >
                <Icon size={15} />
                {label}
              </Link>
            ))}
          </div>

            <div className="relative hidden md:block z-50">
              <form onSubmit={handleSearch} className="flex items-center bg-black/40 border border-white/20 rounded-full px-4 py-1.5 gap-2 hover:border-white/50 transition-all">
                <Search size={14} className="text-netflixLightGray" />
                <input
                  type="text"
                  value={searchVal}
                  onChange={handleSearchChange}
                  onFocus={() => setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                  placeholder="Search movies..."
                  className="bg-transparent text-sm text-white placeholder-netflixGray outline-none w-40 md:w-48 lg:w-56 transition-all"
                />
              </form>

              {/* Suggestions Dropdown */}
              <AnimatePresence>
                {showSuggestions && searchVal.trim().length > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full mt-2 w-full min-w-[300px] right-0 bg-[#181818] border border-white/10 rounded-md shadow-2xl overflow-hidden"
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
                  <div className="w-8 h-8 rounded bg-netflixRed flex items-center justify-center font-bold text-sm">
                    {user.email?.charAt(0).toUpperCase()}
                  </div>
                  <button onClick={handleLogout} className="text-netflixLightGray hover:text-white transition-colors">
                    <LogOut size={18} />
                  </button>
                </div>
              ) : (
                <Link to="/login" className="bg-netflixRed text-white px-4 py-1.5 rounded font-bold text-sm hover:bg-[#c11119] transition">
                  Sign In
                </Link>
              )}
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
