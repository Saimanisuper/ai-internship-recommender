import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

import LandingPage from './pages/LandingPage';
import ProfilePage from './pages/ProfilePage';
import DashboardPage from './pages/DashboardPage';

function App() {
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);

  const handleProfileSubmit = (data) => {
    setProfileData(data);
    navigate('/dashboard');
  };

  return (
    <div className="container">
      <nav className="navbar">
        <div className="logo gradient-text animate-fade-in-up" style={{cursor: 'pointer'}} onClick={() => navigate('/')}>
          <Sparkles size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
          InternMatch AI
        </div>
      </nav>
      
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/profile" element={<ProfilePage onSubmit={handleProfileSubmit} />} />
        <Route path="/dashboard" element={<DashboardPage profileData={profileData} />} />
      </Routes>
    </div>
  );
}

export default App;
