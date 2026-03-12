import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { useApp } from '../store/AppContext';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Heart } from 'lucide-react';

const MOODS = [
  { id: 'romance', label: 'Romance & Love', emoji: '❤️', color: 'from-pink-500 to-rose-600' },
  { id: 'happy', label: 'Laugh Out Loud', emoji: '😂', color: 'from-yellow-400 to-orange-500' },
  { id: 'action', label: 'Action & Thrills', emoji: '🔥', color: 'from-red-600 to-red-800' },
  { id: 'drama', label: 'Deep Drama', emoji: '🎭', color: 'from-purple-600 to-indigo-800' },
  { id: 'adventure', label: 'Sci-Fi & Fantasy', emoji: '✨', color: 'from-blue-500 to-cyan-600' },
  { id: 'horror', label: 'Spooky & Horror', emoji: '👻', color: 'from-gray-700 to-black' },
];

const TasteProfile = () => {
  const { setCurrentMood } = useApp();
  const navigate = useNavigate();

  const handleSelectMood = (moodId) => {
    setCurrentMood(moodId);
    navigate(`/genre/${moodId}`);
  };

  return (
    <div className="bg-netflixDark min-h-screen text-white pb-20 pt-24">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 md:px-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex justify-center mb-4">
            <Heart size={48} className="text-netflixRed" fill="currentColor" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black mb-4">What's your mood?</h1>
          <p className="text-netflixLightGray text-lg">Pick a mood — we'll show you the perfect KDramas for it.</p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 mb-12">
          {MOODS.map(mood => (
            <motion.button
              key={mood.id}
              whileHover={{ scale: 1.06 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleSelectMood(mood.id)}
              className="relative overflow-hidden rounded-xl aspect-square flex flex-col items-center justify-center p-6 border-2 border-transparent hover:border-white/40 transition-all shadow-lg"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${mood.color} opacity-80 z-0`} />
              <div className="absolute inset-0 bg-black/30 z-0" />
              <div className="relative z-10 flex flex-col items-center gap-3">
                <span className="text-5xl md:text-6xl filter drop-shadow-lg">{mood.emoji}</span>
                <span className="font-bold text-lg md:text-xl text-center drop-shadow-md leading-tight">{mood.label}</span>
                <span className="text-white/60 text-xs font-medium mt-1">Tap to explore →</span>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TasteProfile;
