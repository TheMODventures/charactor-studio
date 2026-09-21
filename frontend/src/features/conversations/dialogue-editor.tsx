import { Plus, Trash2, Sparkles, LockKeyhole } from 'lucide-react';
import { useState } from 'react';
import type { Character, ConversationInput, Conversation } from '../../shared/api/types';
import { api } from '../../shared/api/client';
import { ErrorNotice } from '../../shared/components/ui';
export function DialogueEditor({
  value,
  onChange,
  characters,
  saved,
  onLoad,
}: {
  value: ConversationInput;
  onChange: (v: ConversationInput) => void;
  characters: Character[];
  saved: Conversation[];
  onLoad: (c: Conversation) => void;
}) {
  const [topic, setTopic] = useState(''),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>();
  const update = (v: Partial<ConversationInput>) => onChange({ ...value, ...v, approved: false });
  async function draft() {
    setBusy(true);
    setError(null);
    try {
      const result = await api.draft(
        topic,
        characters.slice(0, 2).map((c) => c.id),
      );
      update({ turns: result.turns, mode: 'generated' });
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel dialogue-panel">
      <div className="panel-header">
        <div>
          <span className="step">02</span>
          <h2>The conversation</h2>
        </div>
        <span className="small muted">
          {value.turns.reduce((n, t) => n + t.text.trim().split(/\s+/).filter(Boolean).length, 0)}{' '}
          words
        </span>
      </div>
      <div className="panel-content">
        <div className="field-row">
          <label>
            Conversation title
            <input
              value={value.title}
              onChange={(e) => update({ title: e.target.value })}
              placeholder="A little perspective"
            />
          </label>
          {saved.length > 0 && (
            <label>
              Open saved
              <select
                aria-label="Open saved conversation"
                defaultValue=""
                onChange={(e) => {
                  const c = saved.find((c) => c.id === e.target.value);
                  if (c) onLoad(c);
                }}
              >
                <option value="">Choose a script</option>
                {saved.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        <div className="segmented">
          <button
            className={value.mode === 'scripted' ? 'active' : ''}
            onClick={() => update({ mode: 'scripted' })}
          >
            <LockKeyhole size={14} />
            Write my dialogue
          </button>
          <button
            className={value.mode === 'generated' ? 'active' : ''}
            onClick={() => update({ mode: 'generated' })}
          >
            <Sparkles size={14} />
            Draft with AI
          </button>
        </div>
        {value.mode === 'generated' && (
          <div className="ai-prompt">
            <label>
              What are they talking about?
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Finding joy in the small things…"
              />
            </label>
            <button
              className="button secondary"
              onClick={draft}
              disabled={busy || topic.length < 3 || characters.length < 2}
            >
              {busy ? 'Drafting…' : 'Generate draft'}
            </button>
            <p className="hint">
              Uses your configured Qwen service. Every draft stays editable until you approve it.
            </p>
          </div>
        )}
        <ErrorNotice error={error} />
        <div className="turns">
          {value.turns.map((turn, index) => {
            const c = characters.find((c) => c.id === turn.character_id);
            return (
              <div className="turn" key={index} style={{ borderLeftColor: c?.color || '#ccc' }}>
                <div className="row between">
                  <select
                    aria-label={`Speaker ${index + 1}`}
                    value={turn.character_id}
                    onChange={(e) =>
                      update({
                        turns: value.turns.map((t, i) =>
                          i === index ? { ...t, character_id: e.target.value } : t,
                        ),
                      })
                    }
                  >
                    <option value="" disabled>
                      Choose character
                    </option>
                    {characters.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                  <button
                    className="icon-button"
                    aria-label={`Remove line ${index + 1}`}
                    disabled={value.turns.length === 1}
                    onClick={() => update({ turns: value.turns.filter((_, i) => i !== index) })}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
                <textarea
                  aria-label={`Dialogue line ${index + 1}`}
                  rows={3}
                  value={turn.text}
                  placeholder="What would they say?"
                  onChange={(e) =>
                    update({
                      turns: value.turns.map((t, i) =>
                        i === index ? { ...t, text: e.target.value } : t,
                      ),
                    })
                  }
                />
                <div className="turn-footer">
                  <input
                    aria-label={`Direction ${index + 1}`}
                    placeholder="Performance note, e.g. a knowing smile"
                    value={turn.direction}
                    onChange={(e) =>
                      update({
                        turns: value.turns.map((t, i) =>
                          i === index ? { ...t, direction: e.target.value } : t,
                        ),
                      })
                    }
                  />
                  <label>
                    Pause
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.1"
                      value={turn.pause_after}
                      onChange={(e) =>
                        update({
                          turns: value.turns.map((t, i) =>
                            i === index ? { ...t, pause_after: +e.target.value } : t,
                          ),
                        })
                      }
                    />
                    s
                  </label>
                </div>
              </div>
            );
          })}
        </div>
        <button
          className="add-line"
          onClick={() =>
            update({
              turns: [
                ...value.turns,
                {
                  character_id:
                    characters[value.turns.length % Math.max(1, characters.length)]?.id || '',
                  text: '',
                  direction: '',
                  pause_after: 0.4,
                },
              ],
            })
          }
          disabled={value.turns.length >= 40}
        >
          <Plus size={16} />
          Add dialogue line
        </button>
        <p className="hint">
          Scripted words are preserved. Performance notes stay separate from spoken text.
        </p>
        <label className="check">
          <input
            type="checkbox"
            checked={value.approved}
            onChange={(e) => onChange({ ...value, approved: e.target.checked })}
          />
          I approve these exact words for rendering.
        </label>
      </div>
    </section>
  );
}
