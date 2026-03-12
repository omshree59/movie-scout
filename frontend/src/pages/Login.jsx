import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { auth, db } from '../firebase';
import { doc, setDoc, getDoc } from 'firebase/firestore';

const provider = new GoogleAuthProvider();

const Login = () => {
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;

      // Create user doc in Firestore only if it doesn't exist yet
      const userRef = doc(db, 'users', user.uid);
      const snap = await getDoc(userRef);
      if (!snap.exists()) {
        await setDoc(userRef, {
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
          createdAt: new Date().toISOString(),
          favorites: [],
          watchHistory: [],
          tasteProfile: {},
        });
      }

      navigate('/');
    } catch (err) {
      if (err.code !== 'auth/popup-closed-by-user') {
        setError(err.message.replace('Firebase: ', ''));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col relative">
      {/* Background */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?q=80&w=2500"
          alt="Background"
          className="w-full h-full object-cover opacity-40 filter blur-sm"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/40 to-black" />
      </div>

      {/* Header */}
      <header className="relative z-10 px-4 md:px-8 py-6">
        <Link to="/" className="flex items-center space-x-2">
          <span className="text-netflixRed font-black text-3xl tracking-tight">MOVIE</span>
          <span className="text-white font-black text-3xl tracking-tight">SCOUT</span>
        </Link>
      </header>

      {/* Auth Card */}
      <div className="flex-1 flex items-center justify-center relative z-10 px-4">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-black/80 backdrop-blur-md p-10 md:p-14 rounded-2xl w-full max-w-md border border-white/10 shadow-2xl"
        >
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-full bg-netflixRed/20 flex items-center justify-center">
              <span className="text-3xl">🎬</span>
            </div>
          </div>

          <h1 className="text-3xl font-black mb-2 text-center">Welcome to MovieScout</h1>
          <p className="text-white/50 text-center text-sm mb-8">
            Sign in to rate dramas, manage your list, and get personalized recommendations.
          </p>

          {error && (
            <div className="bg-red-900/60 border border-red-500/40 text-red-200 p-3 rounded-lg mb-6 text-sm text-center">
              {error}
            </div>
          )}

          {/* Google Sign In Button */}
          <motion.button
            onClick={handleGoogleSignIn}
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full flex items-center justify-center gap-3 bg-white text-gray-900 font-bold py-3.5 px-6 rounded-xl text-base hover:bg-gray-100 transition shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {/* Google SVG logo */}
            <svg width="22" height="22" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path fill="#4285F4" d="M47.5 24.5c0-1.6-.1-3.2-.4-4.7H24v8.9h13.2c-.6 3-2.3 5.6-4.9 7.3v6h7.9c4.6-4.3 7.3-10.6 7.3-17.5z"/>
              <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.9-6c-2.1 1.4-4.8 2.2-8 2.2-6.1 0-11.3-4.1-13.2-9.7H2.7v6.2C6.7 42.9 14.8 48 24 48z"/>
              <path fill="#FBBC05" d="M10.8 28.7A14.3 14.3 0 0 1 10.8 19.3V13H2.7A23.9 23.9 0 0 0 0 24c0 3.9.9 7.5 2.7 10.9l8.1-6.2z"/>
              <path fill="#EA4335" d="M24 9.5c3.4 0 6.5 1.2 8.9 3.5l6.6-6.6C35.9 2.5 30.4 0 24 0 14.8 0 6.7 5.1 2.7 13.1l8.1 6.2C12.7 13.6 17.9 9.5 24 9.5z"/>
            </svg>
            {loading ? 'Signing in...' : 'Continue with Google'}
          </motion.button>

          <p className="mt-8 text-xs text-white/30 text-center leading-relaxed">
            By signing in you agree to our Terms of Service.<br />
            Your data is stored securely on Firebase.
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
