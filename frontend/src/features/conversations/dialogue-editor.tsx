import { useState } from 'react';
import { Plus, Trash2, Sparkles } from 'lucide-react';
import type { Character, ConversationInput, Conversation } from '../../shared/api/types';
import { api } from '../../shared/api/client';
import { useCapabilities, unavailable } from '../../shared/api/use-capabilities';
import { UnavailableFeature } from '../../shared/components/unavailable-feature';
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
  const capabilities = useCapabilities();
  const [showAI, setShowAI] = useState(false);
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  const update = (v: Partial<ConversationInput>) => onChange({ ...value, ...v, approved: false });
  async function draft() {
    if (!capabilities.dialogue) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.draft(
        topic,
        characters.slice(0, 2).map((c) => c.id),
      );
      update({ turns: result.turns, mode: 'generated' });
      setShowAI(false);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel simple-dialogue">
      <div className="panel-header">
        <div>
          <span className="step">2</span>
          <h2>Write the conversation</h2>
        </div>
        <UnavailableFeature reason={capabilities.dialogueReason}>
          <button className="button text" onClick={() => setShowAI(!showAI)}>
            <Sparkles size={14} />
            Write with AI
          </button>
        </UnavailableFeature>
      </div>
      <div className="panel-content">
        <p className="small muted">
          Write each character’s exact words below. AI writing is a separate option.
        </p>
        <label>
          Conversation name
          <input
            value={value.title}
            onChange={(e) => update({ title: e.target.value })}
            placeholder="My first conversation"
          />
        </label>
        {saved.length > 0 && (
          <details className="simple-details">
            <summary>Open a saved conversation</summary>
            <select
              aria-label="Open saved conversation"
              defaultValue=""
              onChange={(e) => {
                const script = saved.find((c) => c.id === e.target.value);
                if (script) onLoad(script);
              }}
            >
              <option value="">Choose a conversation</option>
              {saved.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title}
                </option>
              ))}
            </select>
          </details>
        )}
        {showAI && (
          <div className="ai-prompt">
            <label>
              What should they talk about?
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="A topic for the conversation"
              />
            </label>
            <UnavailableFeature reason={capabilities.dialogueReason}>
              <button
                className="button secondary"
                onClick={draft}
                disabled={busy || topic.length < 3 || characters.length !== 2}
              >
                {busy ? 'Writing…' : 'Generate draft'}
              </button>
            </UnavailableFeature>
          </div>
        )}
        <ErrorNotice error={error} />
        <div className="turns">
          {value.turns.map((turn, index) => {
            const character = characters.find((c) => c.id === turn.character_id);
            return (
              <div
                className="turn"
                key={index}
                style={{ borderLeftColor: character?.color || '#ccc' }}
              >
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
                    {!character && turn.character_id && (
                      <option value={turn.character_id} disabled>
                        Choose a character from this scene
                      </option>
                    )}
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
                  rows={2}
                  value={turn.text}
                  placeholder={`What does ${character?.name || 'this character'} say?`}
                  onChange={(e) =>
                    update({
                      turns: value.turns.map((t, i) =>
                        i === index ? { ...t, text: e.target.value } : t,
                      ),
                    })
                  }
                />
              </div>
            );
          })}
        </div>
        <div className="simple-line-actions">
          <button
            className="button secondary"
            disabled={value.turns.length >= 40 || characters.length !== 2}
            onClick={() =>
              update({
                turns: [
                  ...value.turns,
                  {
                    character_id: characters[value.turns.length % 2]?.id || '',
                    text: '',
                    direction: '',
                    pause_after: 0.4,
                  },
                ],
              })
            }
          >
            <Plus size={16} />
            Add line
          </button>
          <span className="small muted">
            {value.turns.reduce((n, t) => n + t.text.trim().split(/\s+/).filter(Boolean).length, 0)}{' '}
            words
          </span>
        </div>
        <details className="simple-details">
          <summary>Delivery options</summary>
          <UnavailableFeature reason={unavailable.performance}>
            <div className="details-content">
              {value.turns.map((turn, index) => (
                <div className="field-row" key={index}>
                  <label>
                    Line {index + 1} · direction
                    <input
                      value={turn.direction}
                      onChange={(e) =>
                        update({
                          turns: value.turns.map((t, i) =>
                            i === index ? { ...t, direction: e.target.value } : t,
                          ),
                        })
                      }
                    />
                  </label>
                  <label>
                    Pause after (seconds)
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
                  </label>
                </div>
              ))}
            </div>
          </UnavailableFeature>
        </details>
        <label className="check">
          <input
            type="checkbox"
            checked={value.approved}
            onChange={(e) => onChange({ ...value, approved: e.target.checked })}
          />
          I approve these exact words for the conversation.
        </label>
      </div>
    </section>
  );
}
