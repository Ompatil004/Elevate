import { useEffect, useState } from 'react';
import {
  adminCreateExercise,
  adminDeleteExercise,
  adminGetExercises,
  adminGetWorkoutRules,
  adminSetWorkoutRules,
  adminUpdateExercise
} from '../../api';
import AdminActionDialog from '../../components/admin/AdminActionDialog';

const EMPTY_FORM = {
  name: '',
  category: '',
  difficulty: 'intermediate',
  description: '',
  equipment: '',
  muscleGroups: '',
  gifUrl: '',
  active: true
};

export default function AdminContent() {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState('');
  const [form, setForm] = useState(EMPTY_FORM);
  const [rulesText, setRulesText] = useState('{}');
  const [jsonError, setJsonError] = useState('');
  const [deleteDialog, setDeleteDialog] = useState({ show: false, exerciseId: '', exerciseName: '' });

  const fetchContent = async () => {
    setLoading(true);
    setError('');

    try {
      const [exerciseRes, rulesRes] = await Promise.all([
        adminGetExercises(),
        adminGetWorkoutRules()
      ]);

      setExercises(exerciseRes.data?.exercises || []);
      setRulesText(JSON.stringify(rulesRes.data?.rules || {}, null, 2));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load content data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, []);

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId('');
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const toList = (raw) =>
    String(raw || '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);

  const buildPayload = () => ({
    name: form.name,
    category: form.category,
    difficulty: form.difficulty,
    description: form.description,
    equipment: toList(form.equipment),
    muscleGroups: toList(form.muscleGroups),
    gifUrl: form.gifUrl,
    active: form.active
  });

  const handleSaveExercise = async (event) => {
    event.preventDefault();
    setError('');

    try {
      const payload = buildPayload();
      if (editingId) {
        await adminUpdateExercise(editingId, payload);
      } else {
        await adminCreateExercise(payload);
      }
      resetForm();
      await fetchContent();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save exercise');
    }
  };

  const handleEdit = (exercise) => {
    setEditingId(exercise._id);
    setForm({
      name: exercise.name || '',
      category: exercise.category || '',
      difficulty: exercise.difficulty || 'intermediate',
      description: exercise.description || '',
      equipment: Array.isArray(exercise.equipment) ? exercise.equipment.join(', ') : '',
      muscleGroups: Array.isArray(exercise.muscleGroups) ? exercise.muscleGroups.join(', ') : '',
      gifUrl: exercise.gifUrl || '',
      active: exercise.active !== false
    });
  };

  const handleDelete = async (id) => {
    const exercise = exercises.find((item) => item._id === id);
    setDeleteDialog({ show: true, exerciseId: id, exerciseName: exercise?.name || 'this exercise' });
  };

  const confirmDeleteExercise = async () => {
    const exerciseId = deleteDialog.exerciseId;
    setDeleteDialog({ show: false, exerciseId: '', exerciseName: '' });
    if (!exerciseId) return;

    try {
      await adminDeleteExercise(exerciseId);
      await fetchContent();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete exercise');
    }
  };

  const handleSaveRules = async () => {
    setError('');

    try {
      const parsed = JSON.parse(rulesText || '{}');
      await adminSetWorkoutRules(parsed);
      await fetchContent();
    } catch (err) {
      setError(err.message || 'Invalid rules JSON');
    }
  };

  return (
    <section>
      <div className="admin-page-head">
        <div>
          <h2>Content Management</h2>
          <p>Maintain exercise library and workout generation rule configuration.</p>
        </div>
        <button className="admin-btn secondary" type="button" onClick={fetchContent}>
          Refresh
        </button>
      </div>

      {error ? <div className="admin-alert">{error}</div> : null}

      <div className="admin-card" style={{ marginBottom: '14px' }}>
        <h3 style={{ marginTop: 0 }}>{editingId ? 'Edit Exercise' : 'Create Exercise'}</h3>

        <form className="admin-inline-form" onSubmit={handleSaveExercise}>
          <div className="admin-inline-2">
            <input className="admin-input" name="name" placeholder="Exercise name" value={form.name} onChange={handleChange} required />
            <input className="admin-input" name="category" placeholder="Category" value={form.category} onChange={handleChange} required />
          </div>

          <div className="admin-inline-2">
            <select className="admin-select" name="difficulty" value={form.difficulty} onChange={handleChange}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <input className="admin-input" name="gifUrl" placeholder="GIF URL (optional)" value={form.gifUrl} onChange={handleChange} />
          </div>

          <textarea className="admin-textarea" name="description" placeholder="Description" value={form.description} onChange={handleChange} />

          <div className="admin-inline-2">
            <input className="admin-input" name="equipment" placeholder="Equipment (comma separated)" value={form.equipment} onChange={handleChange} />
            <input className="admin-input" name="muscleGroups" placeholder="Muscle groups (comma separated)" value={form.muscleGroups} onChange={handleChange} />
          </div>

          <label className="admin-note">
            <input type="checkbox" name="active" checked={form.active} onChange={handleChange} style={{ marginRight: '8px' }} />
            Exercise active
          </label>

          <div className="admin-actions">
            <button className="admin-btn" type="submit">
              {editingId ? 'Update Exercise' : 'Create Exercise'}
            </button>
            {editingId ? (
              <button className="admin-btn secondary" type="button" onClick={resetForm}>
                Cancel Edit
              </button>
            ) : null}
          </div>
        </form>
      </div>

      <div className="admin-card" style={{ marginBottom: '14px' }}>
        <h3 style={{ marginTop: 0 }}>Workout Rules (JSON)</h3>
        <textarea
          className="admin-textarea"
          value={rulesText}
          onChange={(event) => {
            const text = event.target.value;
            setRulesText(text);
            // Validate JSON live so the admin gets immediate feedback
            try {
              JSON.parse(text || '{}');
              setJsonError('');
            } catch (err) {
              setJsonError(`Invalid JSON — ${err.message}`);
            }
          }}
          style={jsonError ? { borderColor: '#ef4444', background: 'rgba(239,68,68,0.04)' } : {}}
        />
        {jsonError && (
          <div style={{
            marginTop: '6px',
            padding: '8px 12px',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '8px',
            color: '#ef4444',
            fontSize: '13px',
            fontFamily: 'monospace'
          }}>
            ⚠️ {jsonError}
          </div>
        )}
        <div style={{ marginTop: '10px' }}>
          <button className="admin-btn" type="button" onClick={handleSaveRules} disabled={!!jsonError}>
            Save Rules
          </button>
          {jsonError && (
            <span style={{ marginLeft: '12px', fontSize: '12px', color: '#71717a' }}>
              Fix the JSON errors above before saving.
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="admin-card">Loading exercises...</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Difficulty</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {exercises.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <div className="admin-empty">No exercises in the library.</div>
                  </td>
                </tr>
              ) : (
                exercises.map((exercise) => (
                  <tr key={exercise._id}>
                    <td data-label="Name">
                      <strong>{exercise.name}</strong>
                      <div className="admin-note">{exercise.description || '-'}</div>
                    </td>
                    <td data-label="Category">{exercise.category || '-'}</td>
                    <td data-label="Difficulty">{exercise.difficulty || '-'}</td>
                    <td data-label="Status">
                      {exercise.active ? (
                        <span className="admin-status ok">Active</span>
                      ) : (
                        <span className="admin-status warn">Inactive</span>
                      )}
                    </td>
                    <td data-label="Actions">
                      <div className="admin-actions">
                        <button className="admin-btn secondary" type="button" onClick={() => handleEdit(exercise)}>
                          Edit
                        </button>
                        <button className="admin-btn danger" type="button" onClick={() => handleDelete(exercise._id)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <AdminActionDialog
        show={deleteDialog.show}
        title="Delete exercise"
        message={`Delete ${deleteDialog.exerciseName}? This action cannot be undone.`}
        confirmLabel="Delete Exercise"
        requirePhrase="DELETE"
        onCancel={() => setDeleteDialog({ show: false, exerciseId: '', exerciseName: '' })}
        onConfirm={confirmDeleteExercise}
      />
    </section>
  );
}
