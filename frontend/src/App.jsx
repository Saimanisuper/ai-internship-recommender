import React, { useMemo, useState } from 'react';
import {
  Bot,
  BriefcaseBusiness,
  FileUp,
  MessageSquareText,
  RefreshCw,
  Send,
  Sparkles,
  UserRound,
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [manualSkills, setManualSkills] = useState('');
  const [parsedProfile, setParsedProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Upload a resume or enter skills. I will rank jobs, explain the fit, and help you plan the next move.',
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  const skills = useMemo(() => {
    if (parsedProfile?.expanded_skills?.length) return parsedProfile.expanded_skills;
    return manualSkills.split(',').map((skill) => skill.trim().toLowerCase()).filter(Boolean);
  }, [manualSkills, parsedProfile]);

  const uploadResume = async () => {
    if (!resumeFile) {
      setStatus('Choose a PDF or text resume first.');
      return;
    }

    setLoading(true);
    setStatus('Parsing resume and matching jobs...');

    try {
      const formData = new FormData();
      formData.append('file', resumeFile);
      const response = await fetch(`${API_URL}/upload_resume`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Resume upload failed.');
      }

      const data = await response.json();
      setParsedProfile(data);
      setRecommendations(data.recommendations || []);
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: `I found ${data.skills.length} resume skills and ranked ${data.recommendations.length} jobs. Your strongest signals are ${data.skills.slice(0, 6).join(', ') || 'still emerging'}.`,
        },
      ]);
      setStatus('Resume parsed successfully.');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const runManualRecommendation = async () => {
    if (!skills.length) {
      setStatus('Add at least one skill.');
      return;
    }

    setLoading(true);
    setStatus('Ranking jobs...');

    try {
      const response = await fetch(`${API_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, interests: [], education: '', limit: 8 }),
      });

      if (!response.ok) throw new Error('Recommendation request failed.');

      const data = await response.json();
      setRecommendations(data);
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: `I ranked ${data.length} jobs from your typed skills: ${skills.slice(0, 8).join(', ')}.`,
        },
      ]);
      setStatus('Recommendations ready.');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (event) => {
    event.preventDefault();
    const text = chatInput.trim();
    if (!text) return;

    setChatInput('');
    setMessages((current) => [...current, { role: 'user', text }]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, skills, recommendations }),
      });

      if (!response.ok) throw new Error('Chat request failed.');

      const data = await response.json();
      setMessages((current) => [...current, { role: 'assistant', text: data.response }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: error.message }]);
    }
  };

  const refreshJobs = async () => {
    setLoading(true);
    setStatus('Refreshing in-memory job index...');
    try {
      const response = await fetch(`${API_URL}/refresh_jobs`, { method: 'POST' });
      if (!response.ok) throw new Error('Refresh failed.');
      const data = await response.json();
      setStatus(`Job index refreshed with ${data.jobs} jobs.`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <button className="brand-button" type="button" aria-label="AI Job Match home">
          <Sparkles size={22} />
          <span>AI Job Match</span>
        </button>
        <button className="icon-button" type="button" onClick={refreshJobs} title="Refresh jobs">
          <RefreshCw size={19} />
        </button>
      </header>

      <section className="workspace">
        <aside className="control-panel">
          <div className="panel-header">
            <FileUp size={22} />
            <div>
              <h1>Resume Intake</h1>
              <p>PDF or text resume, then optional manual skills.</p>
            </div>
          </div>

          <label className="upload-zone">
            <input
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
            />
            <FileUp size={28} />
            <span>{resumeFile?.name || 'Choose resume'}</span>
          </label>

          <button className="primary-action" type="button" onClick={uploadResume} disabled={loading}>
            <Sparkles size={18} />
            Parse Resume
          </button>

          <div className="divider" />

          <label className="field-label" htmlFor="manual-skills">Manual skills</label>
          <textarea
            id="manual-skills"
            value={manualSkills}
            onChange={(event) => setManualSkills(event.target.value)}
            placeholder="python, sql, react, docker"
          />
          <button className="secondary-action" type="button" onClick={runManualRecommendation} disabled={loading}>
            <BriefcaseBusiness size={18} />
            Recommend
          </button>

          {status && <p className="status-line">{status}</p>}

          <div className="skills-bank">
            <h2>Extracted Skills</h2>
            <div className="tags-group">
              {skills.length ? skills.slice(0, 20).map((skill) => (
                <span className="skill-tag" key={skill}>{skill}</span>
              )) : <span className="muted">No skills yet</span>}
            </div>
          </div>
        </aside>

        <section className="chat-panel">
          <div className="chat-header">
            <MessageSquareText size={22} />
            <h2>Career Assistant</h2>
          </div>

          <div className="message-list">
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
                <span className="avatar">{message.role === 'assistant' ? <Bot size={17} /> : <UserRound size={17} />}</span>
                <p>{message.text}</p>
              </div>
            ))}

            {recommendations.length > 0 && (
              <div className="jobs-stream">
                {recommendations.map((job) => (
                  <article className="job-card" key={`${job.id}-${job.role}`}>
                    <div className="job-card-head">
                      <div>
                        <h3>{job.role}</h3>
                        <p>{job.company} · {job.location}</p>
                      </div>
                      <strong>{Math.round(job.match_score * 100)}%</strong>
                    </div>
                    <p className="job-explanation">{job.explanation}</p>
                    <div className="tags-group">
                      {job.matched_skills.map((skill) => (
                        <span className="skill-tag match" key={`${job.id}-${skill}`}>{skill}</span>
                      ))}
                      {job.missing_skills.map((skill) => (
                        <span className="skill-tag missing" key={`${job.id}-${skill}`}>{skill}</span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>

          <form className="chat-form" onSubmit={sendMessage}>
            <input
              value={chatInput}
              onChange={(event) => setChatInput(event.target.value)}
              placeholder="Ask why this job fits, what to learn next, or show top matches"
            />
            <button className="send-button" type="submit" title="Send">
              <Send size={19} />
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}

export default App;
