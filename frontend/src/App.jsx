import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Search from './pages/Search';
import Dashboard from './pages/Dashboard';
import MovieDetails from './pages/MovieDetails';
import TasteProfile from './pages/TasteProfile';
import Login from './pages/Login';
import GenrePage from './pages/GenrePage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-netflixDark text-white selection:bg-netflixRed selection:text-white">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/search" element={<Search />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/taste-profile" element={<TasteProfile />} />
          <Route path="/genre/:mood" element={<GenrePage />} />
          <Route path="/movie/:id" element={<MovieDetails />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
