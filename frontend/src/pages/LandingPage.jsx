import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BrainCircuit } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page animate-fade-in-up">
      <div className="animate-float" style={{ marginBottom: '2rem' }}>
        <BrainCircuit size={64} color="var(--primary-color)" />
      </div>
      <h1>
        Discover Your Pure <br />
        <span className="gradient-text">Potential Internships</span>
      </h1>
      <p>
        Harness the power of AI to match your unique skills and interests with the perfect internship opportunities. No generic searches—just hyper-personalized recommendations.
      </p>
      
      <button className="btn-primary" onClick={() => navigate('/profile')}>
        Get Started <ArrowRight size={18} />
      </button>
    </div>
  );
}
