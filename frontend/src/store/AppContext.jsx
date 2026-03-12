import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '../firebase';

const AppContext = createContext();

export const useApp = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [user, setUser]             = useState(null);
  const [userId, setUserId]         = useState('demo_user');
  const [authLoading, setAuthLoading] = useState(true);
  // Called when a protected action requires sign-in (set by pages that need it)
  const [onAuthRequired, setOnAuthRequired] = useState(() => () => {});

  const [favorites, setFavorites] = useState(() => {
    try { return JSON.parse(localStorage.getItem('moviescout_favorites') || '[]'); }
    catch { return []; }
  });
  const [watchHistory, setWatchHistory] = useState([]);
  const [currentMood, setCurrentMood]   = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setUserId(currentUser ? currentUser.uid : 'demo_user');
      setAuthLoading(false);
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    localStorage.setItem('moviescout_favorites', JSON.stringify(favorites));
  }, [favorites]);

  const logout = useCallback(() => signOut(auth), []);

  /**
   * toggleFavorite — requires auth.
   * If unauthenticated, calls onAuthRequired() instead of modifying state.
   */
  const toggleFavorite = useCallback((movie) => {
    if (!user) {
      onAuthRequired();
      return;
    }
    setFavorites(prev => {
      const exists = prev.find(m => m.movie_id === movie.movie_id);
      if (exists) return prev.filter(m => m.movie_id !== movie.movie_id);
      return [...prev, movie];
    });
  }, [user, onAuthRequired]);

  const isFavorite = useCallback(
    (movieId) => favorites.some(m => String(m.movie_id) === String(movieId)),
    [favorites]
  );

  return (
    <AppContext.Provider value={{
      user, authLoading, logout,
      userId, setUserId,
      favorites, toggleFavorite, isFavorite,
      watchHistory, setWatchHistory,
      currentMood, setCurrentMood,
      setOnAuthRequired,
    }}>
      {children}
    </AppContext.Provider>
  );
};
