import { useCallback, useRef, useState } from 'react';

// Smart career assistant using intelligent pattern matching and templates
// This provides a rich chat experience without any API costs

const CAREER_KNOWLEDGE = {
  skills: {
    python: {
      related: ['data analysis', 'machine learning', 'automation', 'backend development'],
      learning: ['codecademy', 'python.org tutorials', 'automate the boring stuff'],
      roles: ['data scientist', 'backend engineer', 'ml engineer', 'devops engineer'],
    },
    javascript: {
      related: ['web development', 'frontend', 'react', 'node.js'],
      learning: ['freecodecamp', 'javascript.info', 'eloquent javascript'],
      roles: ['frontend developer', 'full stack engineer', 'web developer'],
    },
    react: {
      related: ['frontend', 'ui development', 'component design', 'state management'],
      learning: ['react.dev', 'scrimba', 'frontend masters'],
      roles: ['frontend developer', 'react developer', 'ui engineer'],
    },
    sql: {
      related: ['data analysis', 'database management', 'reporting', 'business intelligence'],
      learning: ['sqlzoo', 'mode analytics sql tutorial', 'datacamp'],
      roles: ['data analyst', 'database administrator', 'business analyst'],
    },
    java: {
      related: ['enterprise development', 'android', 'backend systems'],
      learning: ['oracle java tutorials', 'codecademy java', 'mooc.fi'],
      roles: ['software engineer', 'android developer', 'backend engineer'],
    },
    'machine learning': {
      related: ['data science', 'ai', 'deep learning', 'statistics'],
      learning: ['coursera ml course', 'fast.ai', 'kaggle learn'],
      roles: ['ml engineer', 'data scientist', 'ai researcher'],
    },
    docker: {
      related: ['devops', 'containers', 'deployment', 'kubernetes'],
      learning: ['docker docs', 'play with docker', 'docker mastery course'],
      roles: ['devops engineer', 'sre', 'platform engineer'],
    },
    aws: {
      related: ['cloud computing', 'infrastructure', 'serverless'],
      learning: ['aws training', 'cloud guru', 'aws skill builder'],
      roles: ['cloud engineer', 'solutions architect', 'devops engineer'],
    },
  },

  interviewTips: [
    'Research the company thoroughly - understand their products, culture, and recent news',
    'Prepare STAR method stories for behavioral questions (Situation, Task, Action, Result)',
    'Practice coding problems on LeetCode or HackerRank for technical roles',
    'Prepare thoughtful questions to ask your interviewers about the role and team',
    'Review your resume and be ready to discuss every project in detail',
    'Practice explaining technical concepts simply - imagine teaching a beginner',
    'Set up a professional background and test your tech for video interviews',
    'Send a thank-you email within 24 hours after each interview',
  ],

  portfolioTips: [
    'Include 3-5 quality projects rather than many incomplete ones',
    'Write clear README files explaining project purpose, tech stack, and how to run it',
    'Deploy your projects so recruiters can see them live',
    'Include diverse projects showing different skills and problem-solving',
    'Add a personal touch - projects solving real problems you care about stand out',
    'Keep your GitHub profile active with regular commits',
    'Include links to live demos, not just source code',
  ],

  networkingTips: [
    'Connect with recruiters at target companies on LinkedIn',
    'Attend virtual meetups and tech conferences in your field',
    'Contribute to open source projects to build visibility',
    'Write blog posts or create content about what you\'re learning',
    'Reach out to alumni from your school working in your target industry',
    'Join Discord or Slack communities for your tech stack',
    'Ask for informational interviews, not just job referrals',
  ],
};

function analyzeIntent(message) {
  const lower = message.toLowerCase();
  
  if (lower.includes('why') && (lower.includes('match') || lower.includes('fit') || lower.includes('recommend'))) {
    return 'explain_match';
  }
  if (lower.includes('learn') || lower.includes('improve') || lower.includes('gap') || lower.includes('skill')) {
    return 'learning_path';
  }
  if (lower.includes('interview') || lower.includes('prepare')) {
    return 'interview';
  }
  if (lower.includes('portfolio') || lower.includes('project') || lower.includes('github')) {
    return 'portfolio';
  }
  if (lower.includes('network') || lower.includes('connect') || lower.includes('linkedin')) {
    return 'networking';
  }
  if (lower.includes('top') || lower.includes('best') || lower.includes('rank')) {
    return 'top_matches';
  }
  if (lower.includes('salary') || lower.includes('pay') || lower.includes('compensation')) {
    return 'salary';
  }
  if (lower.includes('resume') || lower.includes('cv')) {
    return 'resume_tips';
  }
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey') || lower.includes('help')) {
    return 'greeting';
  }
  
  return 'general';
}

function generateResponse(message, skills, recommendations) {
  const intent = analyzeIntent(message);
  const topJob = recommendations[0];
  const userSkillsSet = new Set(skills.map(s => s.toLowerCase()));
  
  switch (intent) {
    case 'greeting':
      return generateGreeting(skills, recommendations);
    case 'explain_match':
      return generateMatchExplanation(topJob, skills);
    case 'learning_path':
      return generateLearningPath(message, skills, recommendations);
    case 'interview':
      return generateInterviewAdvice(topJob);
    case 'portfolio':
      return generatePortfolioAdvice(skills, topJob);
    case 'networking':
      return generateNetworkingAdvice(topJob);
    case 'top_matches':
      return generateTopMatches(recommendations);
    case 'salary':
      return generateSalaryInfo(topJob);
    case 'resume_tips':
      return generateResumeTips(skills, recommendations);
    default:
      return generateGeneralResponse(message, skills, recommendations);
  }
}

function generateGreeting(skills, recommendations) {
  if (!skills.length) {
    return "Hello! I'm your AI career assistant. Upload your resume or enter your skills, and I'll help you find matching internships, identify skill gaps, and prepare for your job search. What would you like to explore?";
  }
  
  const topSkills = skills.slice(0, 3).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ');
  return `Hello! I see you have skills in ${topSkills}. I've analyzed ${recommendations.length} potential matches for you. Ask me about why specific jobs match, what skills to learn next, or how to prepare for interviews!`;
}

function generateMatchExplanation(job, skills) {
  if (!job) {
    return "I don't have any job recommendations to explain yet. Upload your resume or add skills first, and I'll show you why specific internships match your profile.";
  }
  
  const matched = job.matched_skills || [];
  const missing = job.missing_skills || [];
  const score = Math.round((job.match_score || 0) * 100);
  
  let response = `**${job.role} at ${job.company}** (${score}% match)\n\n`;
  
  if (matched.length) {
    response += `**Why you're a fit:** Your experience with ${matched.slice(0, 4).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ')} directly aligns with what they're looking for. `;
  }
  
  if (missing.length) {
    response += `\n\n**To strengthen your application:** Focus on gaining experience with ${missing.slice(0, 3).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ')}. `;
    
    // Add specific learning resources if we know the skill
    const firstMissing = missing[0]?.toLowerCase();
    const skillInfo = CAREER_KNOWLEDGE.skills[firstMissing];
    if (skillInfo) {
      response += `Check out ${skillInfo.learning.slice(0, 2).join(' or ')} to get started.`;
    }
  }
  
  return response;
}

function generateLearningPath(message, skills, recommendations) {
  const missingSkills = new Set();
  recommendations.slice(0, 5).forEach(job => {
    (job.missing_skills || []).forEach(skill => missingSkills.add(skill.toLowerCase()));
  });
  
  if (!missingSkills.size) {
    return "Great news! Your skills already cover most of what these roles require. Focus on building portfolio projects that demonstrate these skills in action, and practice articulating your experience in interviews.";
  }
  
  const prioritySkills = Array.from(missingSkills).slice(0, 4);
  let response = `**Recommended Learning Path:**\n\n`;
  
  prioritySkills.forEach((skill, index) => {
    const skillInfo = CAREER_KNOWLEDGE.skills[skill];
    response += `${index + 1}. **${skill.charAt(0).toUpperCase() + skill.slice(1)}**`;
    if (skillInfo) {
      response += ` - Learn at: ${skillInfo.learning[0]}`;
    }
    response += '\n';
  });
  
  response += `\nStart with ${prioritySkills[0]} as it appears most frequently in your top matches. Dedicate 2-3 weeks to each skill, building small projects along the way.`;
  
  return response;
}

function generateInterviewAdvice(job) {
  const tips = CAREER_KNOWLEDGE.interviewTips;
  const randomTips = tips.sort(() => 0.5 - Math.random()).slice(0, 4);
  
  let response = '**Interview Preparation Tips:**\n\n';
  
  randomTips.forEach((tip, index) => {
    response += `${index + 1}. ${tip}\n`;
  });
  
  if (job) {
    response += `\n**For ${job.role} specifically:** Research ${job.company}'s recent work and be ready to discuss how your experience with ${(job.matched_skills || []).slice(0, 2).join(' and ')} applies to their challenges.`;
  }
  
  return response;
}

function generatePortfolioAdvice(skills, job) {
  const tips = CAREER_KNOWLEDGE.portfolioTips;
  const randomTips = tips.sort(() => 0.5 - Math.random()).slice(0, 4);
  
  let response = '**Portfolio Building Advice:**\n\n';
  
  randomTips.forEach((tip, index) => {
    response += `${index + 1}. ${tip}\n`;
  });
  
  if (skills.length) {
    const projectIdeas = generateProjectIdeas(skills);
    response += `\n**Project Ideas for Your Skills:**\n${projectIdeas}`;
  }
  
  return response;
}

function generateProjectIdeas(skills) {
  const skillsLower = skills.map(s => s.toLowerCase());
  const ideas = [];
  
  if (skillsLower.some(s => s.includes('python') || s.includes('data'))) {
    ideas.push('- Data analysis dashboard with visualization');
  }
  if (skillsLower.some(s => s.includes('react') || s.includes('javascript'))) {
    ideas.push('- Interactive web app with API integration');
  }
  if (skillsLower.some(s => s.includes('machine learning') || s.includes('ml'))) {
    ideas.push('- ML model with a simple prediction interface');
  }
  if (skillsLower.some(s => s.includes('sql') || s.includes('database'))) {
    ideas.push('- Full-stack app with database CRUD operations');
  }
  
  if (!ideas.length) {
    ideas.push('- Build a tool that solves a problem you personally face');
    ideas.push('- Recreate a feature from an app you admire');
  }
  
  return ideas.join('\n');
}

function generateNetworkingAdvice(job) {
  const tips = CAREER_KNOWLEDGE.networkingTips;
  const randomTips = tips.sort(() => 0.5 - Math.random()).slice(0, 4);
  
  let response = '**Networking Strategies:**\n\n';
  
  randomTips.forEach((tip, index) => {
    response += `${index + 1}. ${tip}\n`;
  });
  
  if (job) {
    response += `\n**For ${job.company}:** Look for their engineers on LinkedIn, check if they have a tech blog, and see if their team members speak at conferences or meetups.`;
  }
  
  return response;
}

function generateTopMatches(recommendations) {
  if (!recommendations.length) {
    return "I don't have any matches to show yet. Upload your resume or add skills to see your top internship recommendations!";
  }
  
  let response = '**Your Top Matches:**\n\n';
  
  recommendations.slice(0, 5).forEach((job, index) => {
    const score = Math.round((job.match_score || 0) * 100);
    const matchedCount = (job.matched_skills || []).length;
    response += `${index + 1}. **${job.role}** at ${job.company} - ${score}% match (${matchedCount} skills aligned)\n`;
  });
  
  response += '\nAsk me about any specific role to learn why it matches and how to prepare!';
  
  return response;
}

function generateSalaryInfo(job) {
  return `While I don't have specific salary data, here are some tips for internship compensation:\n\n1. **Research on Glassdoor and Levels.fyi** for company-specific data\n2. **Location matters** - Bay Area and NYC typically pay more but have higher costs\n3. **Tech internships** generally range from $25-60/hour depending on company size\n4. **Consider the full package** - housing stipends, relocation, return offer potential\n\n${job ? `For ${job.company}, I'd recommend checking their Glassdoor reviews for intern compensation details.` : ''}`;
}

function generateResumeTips(skills, recommendations) {
  let response = '**Resume Optimization Tips:**\n\n';
  response += '1. **Quantify achievements** - Use numbers: "Improved performance by 40%"\n';
  response += '2. **Match keywords** - Include skills from job descriptions\n';
  response += '3. **Lead with impact** - Start bullets with action verbs\n';
  response += '4. **Keep it concise** - One page for internships\n';
  
  if (recommendations.length) {
    const commonSkills = new Set();
    recommendations.slice(0, 3).forEach(job => {
      (job.skills_required || []).forEach(s => commonSkills.add(s));
    });
    
    const topRequired = Array.from(commonSkills).slice(0, 5);
    if (topRequired.length) {
      response += `\n**Ensure these appear on your resume:** ${topRequired.join(', ')}`;
    }
  }
  
  return response;
}

function generateGeneralResponse(message, skills, recommendations) {
  const topJob = recommendations[0];
  
  if (!skills.length && !recommendations.length) {
    return "I'm here to help with your job search! You can:\n\n- **Upload your resume** to get personalized job matches\n- **Enter skills manually** to see relevant opportunities\n- **Ask me** about interview prep, portfolio building, or networking\n\nWhat would you like to start with?";
  }
  
  if (topJob) {
    const matched = (topJob.matched_skills || []).slice(0, 3).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ');
    const missing = (topJob.missing_skills || []).slice(0, 2).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ');
    
    return `Based on your profile, **${topJob.role} at ${topJob.company}** is your strongest match. Your ${matched || 'experience'} aligns well. ${missing ? `Consider building skills in ${missing} to strengthen your application.` : 'You\'re well-positioned for this role!'}\n\nI can help you with:\n- Understanding why jobs match\n- Creating a learning path\n- Interview preparation\n- Portfolio advice`;
  }
  
  return "I can help you explore career opportunities! Try asking:\n- \"Why does this job match my profile?\"\n- \"What skills should I learn next?\"\n- \"How do I prepare for interviews?\"\n- \"Show me my top matches\"";
}

export function useLocalAI() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isModelLoaded] = useState(true); // No model loading needed for rule-based
  
  const generateResponseAsync = useCallback(async (message, skills = [], recommendations = []) => {
    setIsProcessing(true);
    
    try {
      // Small delay to feel more natural
      await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 400));
      
      const response = generateResponse(message, skills, recommendations);
      return response;
    } finally {
      setIsProcessing(false);
    }
  }, []);
  
  return {
    generateResponse: generateResponseAsync,
    isProcessing,
    isModelLoaded,
  };
}
