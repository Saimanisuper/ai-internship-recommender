import React, { useState } from 'react';
import { ArrowRight } from 'lucide-react';

export default function ProfilePage({ onSubmit }) {
  // State initialization for tracking user input fields
  const [skills, setSkills] = useState('');
  const [interests, setInterests] = useState('');
  const [education, setEducation] = useState('');

  /**
   * Handles the form submission event, processing the raw comma-separated strings 
   * into clean arrays for our Machine Learning backend.
   * 
   * @param {React.FormEvent} e Base HTML form event.
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Parse comma-separated strings, trim whitespaces and filter any empty strings
    const skillsArray = skills.split(',').map(s => s.trim()).filter(Boolean);
    const interestsArray = interests.split(',').map(i => i.trim()).filter(Boolean);
    
    // Fire the parent-provided callback bridging state out into the App router structure
    onSubmit({
      skills: skillsArray,
      interests: interestsArray,
      education: education.trim()
    });
  };

  return (
    <div className="profile-page animate-fade-in-up">
      <div className="glass-panel profile-form-container">
        <h2>Build Your Profile</h2>
        <p>Tell the AI about your background to find the absolute best match.</p>
        
        <form onSubmit={handleSubmit}>
          
          {/* Main Technical Requirements input block */}
          <div className="input-group">
            <label htmlFor="skills">Technical Skills (comma separated)</label>
            <input 
              type="text" 
              id="skills"
              className="input-field" 
              placeholder="e.g. Python, React, Machine Learning"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              required
            />
          </div>
          
          {/* Optional qualitative context for mapping broader themes */}
          <div className="input-group">
            <label htmlFor="interests">Interests (optional)</label>
            <input 
              type="text" 
              id="interests"
              className="input-field" 
              placeholder="e.g. AI, Web Development, Fintech"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
            />
          </div>
          
          {/* Base academic tracker */}
          <div className="input-group">
            <label htmlFor="education">Education</label>
            <input 
              type="text" 
              id="education"
              className="input-field" 
              placeholder="e.g. B.Tech Computer Science"
              value={education}
              onChange={(e) => setEducation(e.target.value)}
            />
          </div>
          
          <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
            Get Recommendations <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
