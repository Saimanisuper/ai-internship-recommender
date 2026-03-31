import React from 'react';
import { Building2, MapPin } from 'lucide-react';

export default function InternshipCard({ data }) {
  const { role, company, match_score, matched_skills, missing_skills, explanation, location } = data;
  
  // Calculate percentage format for score (e.g. 0.82 -> 82%)
  const displayScore = Math.round(match_score * 100);
  
  // Determine color class based on score
  let scoreClass = 'score-low';
  if (displayScore >= 70) scoreClass = 'score-high';
  else if (displayScore >= 40) scoreClass = 'score-medium';

  return (
    <div className="glass-panel internship-card">
      <div className="card-header">
        <div className="card-title-group">
          <h3 className="card-role">{role}</h3>
          <div className="card-company">
            <Building2 size={14} /> {company} • <MapPin size={14} style={{marginLeft: '0.25rem'}}/> <span style={{textTransform: 'capitalize'}}>{location || 'Remote'}</span>
          </div>
        </div>
        <div className={`match-score ${scoreClass}`}>
          {displayScore}%
        </div>
      </div>

      <div className="skills-section">
        {matched_skills && matched_skills.length > 0 && (
          <div>
            <span className="skills-label">Matched Skills</span>
            <div className="tags-group" style={{marginTop:'0.5rem'}}>
              {matched_skills.map((skill, i) => (
                <span key={`match-${i}`} className="tag match">{skill}</span>
              ))}
            </div>
          </div>
        )}

        {missing_skills && missing_skills.length > 0 && (
          <div>
            <span className="skills-label">Missing Skills</span>
            <div className="tags-group" style={{marginTop:'0.5rem'}}>
              {missing_skills.map((skill, i) => (
                <span key={`miss-${i}`} className="tag missing">{skill}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="explanation-box">
        {explanation}
      </div>
    </div>
  );
}
