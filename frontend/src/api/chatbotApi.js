import { FitnessAPI } from './apiClient';

const _pickChatProfile = (profile, includeSensitive = false) => {
  if (!profile || typeof profile !== 'object') return {};

  const compact = {
    goal: profile.goal,
    experience: profile.experience,
    activity_level: profile.activity_level,
    dietary_preference: profile.dietary_preference,
    equipment: Array.isArray(profile.equipment) ? profile.equipment.slice(0, 12) : [],
  };

  if (includeSensitive) {
    compact.age = profile.age;
    compact.weight = profile.weight;
    compact.height = profile.height;
    compact.allergies = Array.isArray(profile.allergies) ? profile.allergies.slice(0, 12) : [];
    compact.body_issues = Array.isArray(profile.body_issues) ? profile.body_issues.slice(0, 12) : [];
  }

  return Object.fromEntries(
    Object.entries(compact).filter(([, value]) => {
      if (Array.isArray(value)) return value.length > 0;
      return value !== undefined && value !== null && String(value).trim() !== '';
    })
  );
};

export const sendChatbotMessage = (message, profile, history, options = {}) => {
  const includeSensitive = options.includeSensitive === true;

  const sanitizedHistory = (Array.isArray(history) ? history : [])
    .filter((msg) => msg && typeof msg === 'object' && msg.role && msg.text)
    .slice(-50)
    .map(({ role, text }) => ({ role: String(role), content: String(text) }));

  return FitnessAPI.post(
    '/api/chat',
    {
      message,
      profile: _pickChatProfile(profile, includeSensitive),
      history: sanitizedHistory,
      consent_to_health_processing: includeSensitive,
    },
    { timeout: 90000 }
  );
};

export const getHealth = () => FitnessAPI.get('/health', { timeout: 15000 });
