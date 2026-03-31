import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InternshipCard from '../components/InternshipCard';
import { Sparkles } from 'lucide-react';

export default function DashboardPage({ profileData }) {
  const navigate = useNavigate();
  
  // Asynchronous View State Variables
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  /**
   * Triggers the API interaction bridging the Frontend state query 
   * block against the Backend ML scoring block automatically upon render.
   */
  useEffect(() => {
    // Validates if user navigated directly without creating a profile first.
    if (!profileData || profileData.skills.length === 0) {
      navigate('/profile');
      return;
    }

    const fetchRecommendations = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/recommend`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileData),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch recommendations from the Engine.');
        }

        const data = await response.json();
        setResults(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [profileData, navigate]);

  /** Rendering Logic Map **/

  // 1. Awaiting Network Call & Model execution time (spinning loader)
  if (loading) {
    return (
      <div className="landing-page">
        <div className="loader"></div>
        <p style={{ marginTop: '2rem' }}>Running Core AI Models...</p>
      </div>
    );
  }

  // 2. Fetch Exception / Cross-Origin Failure Guard Clause
  if (error) {
    return (
      <div className="container">
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h2 style={{ color: 'var(--tag-missing-text)' }}>Connection Error</h2>
          <p>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/profile')} style={{ marginTop: '1rem' }}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // 3. Fully Success State / Rendering of ranked Internship listings.
  return (
    <div className="dashboard-page animate-fade-in-up">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: 0 }}>Your Recommendations</h2>
        <Sparkles size={24} color="var(--primary-color)" />
      </div>

      {/* Fallback if zero roles possess a matching similarity score string > 0 */}
      {results.length === 0 ? (
        <div className="empty-state">
          <p>No suitable matches found for your current profile. Try adding more technical skills or generic interests.</p>
          <button className="btn-primary" onClick={() => navigate('/profile')}>
            Edit Profile
          </button>
        </div>
      ) : (
        <div className="results-grid">
          {results.map((internship, index) => (
            <InternshipCard key={index} data={internship} />
          ))}
        </div>
      )}
    </div>
  );
}
