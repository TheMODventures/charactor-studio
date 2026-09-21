import { UnavailableFeature } from '../../shared/components/unavailable-feature';
import { useCapabilities } from '../../shared/api/use-capabilities';
import { useEffect, useState, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Check, Clapperboard, Save, SlidersHorizontal } from 'lucide-react';
import { api } from '../../shared/api/client';
import type { ConversationInput, SceneInput, Character } from '../../shared/api/types';
import { Avatar, ErrorNotice, PageTitle, Loading } from '../../shared/components/ui';
import { SceneEditor } from '../scenes/scene-editor';
import { DialogueEditor } from '../conversations/dialogue-editor';
import { CharacterEditor } from '../characters/character-editor';
export function StudioPage() {
  const capabilities = useCapabilities();
  const chars = useQuery({ queryKey: ['characters'], queryFn: api.characters }),
    scripts = useQuery({ queryKey: ['conversations'], queryFn: api.conversations }),
    scenes = useQuery({ queryKey: ['scenes'], queryFn: api.scenes }),
    status = useQuery({ queryKey: ['system'], queryFn: api.status });
  const characters = chars.data?.filter((c) => !c.archived) || [];
  const [script, setScript] = useState<ConversationInput>({
      title: 'A little perspective',
      mode: 'scripted',
      approved: false,
      turns: [
        { character_id: '', text: '', direction: '', pause_after: 0.4 },
        { character_id: '', text: '', direction: '', pause_after: 0.4 },
      ],
    }),
    [scene, setScene] = useState<SceneInput>({
      name: 'The living room',
      image_asset_id: '',
      character_ids: ['', ''],
      prompt:
        'Two women seated together in a warm living room. Natural eye contact, subtle gestures and attentive listening while the other speaks.',
      approved: false,
    });
  const [scriptId, setScriptId] = useState<string>(),
    [sceneId, setSceneId] = useState<string>(),
    [kind, setKind] = useState('storyboard'),
    [seconds, setSeconds] = useState(60),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>(),
    [notice, setNotice] = useState(''),
    [editing, setEditing] = useState<Character>();
  const query = useQueryClient(),
    navigate = useNavigate();
  const initialScene = useRef(false);
  useEffect(() => {
    if (!initialScene.current && scenes.data) {
      initialScene.current = true;
      const demo = scenes.data.find((s) => s.id === 'demo-scene');
      if (demo) {
        setScene({ ...demo, approved: false });
        setSceneId(demo.id);
      }
    }
  }, [scenes.data]);
  useEffect(() => {
    if (chars.data?.length) {
      const ids = chars.data
        .filter((c) => !c.archived)
        .slice(0, 2)
        .map((c) => c.id);
      setScript((s) => ({
        ...s,
        turns: s.turns.map((t, i) => ({
          ...t,
          character_id: t.character_id || ids[i % ids.length] || '',
        })),
      }));
      setScene((s) => ({
        ...s,
        character_ids: s.character_ids.map((id, i) => id || ids[i] || ''),
      }));
    }
  }, [chars.data]);
  async function save(render = false) {
    if (render && (capabilities.workerReason || (kind === 'animated' && !capabilities.animation)))
      return;
    setBusy(true);
    setError(null);
    setNotice('');
    try {
      const conversation = await api.saveConversation(script, scriptId);
      setScriptId(conversation.id);
      await query.invalidateQueries({ queryKey: ['conversations'] });
      let savedScene;
      if (scene.image_asset_id) {
        savedScene = await api.saveScene(scene, sceneId);
        setSceneId(savedScene.id);
        await query.invalidateQueries({ queryKey: ['scenes'] });
      }
      if (render) {
        if (!savedScene) throw new Error('Upload and approve a shared scene first.');
        await api.generate(conversation.id, savedScene.id, kind, seconds);
        await query.invalidateQueries({ queryKey: ['generations'] });
        navigate('/renders');
      } else setNotice('Changes saved. Your characters and script are ready to reuse.');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  const ready =
    script.approved &&
    scene.approved &&
    !!scene.image_asset_id &&
    scene.character_ids[0] !== scene.character_ids[1] &&
    script.turns.every((t) => t.text.trim() && t.character_id);
  if (chars.isLoading) return <Loading />;
  return (
    <>
      <PageTitle
        eyebrow="THE CREATOR WORKSPACE"
        title="Give your characters a moment."
        description="Bring two original personalities into one conversation."
        action={
          <span className="pill outline">
            <span className="dot" />
            Original characters only
          </span>
        }
      />
      <ErrorNotice error={chars.error || scripts.error || scenes.error || error} />
      {notice && (
        <div className="notice success" role="status">
          <Check size={16} />
          {notice}
        </div>
      )}
      <div className="cast-strip">
        <div className="cast-label">
          <span className="eyebrow">IN THIS SCENE</span>
          <strong>Your cast</strong>
        </div>
        {scene.character_ids
          .map((id) => characters.find((c) => c.id === id))
          .filter((c): c is Character => !!c)
          .map((c) => (
            <button className="cast-person" key={c.id} onClick={() => setEditing(c)}>
              <Avatar character={c} />
              <span>
                <strong>{c.name}</strong>
                <small>{c.description}</small>
              </span>
              <SlidersHorizontal size={15} />
            </button>
          ))}
        <span className="cast-note">
          Individual voices.
          <br />
          Shared chemistry.
        </span>
      </div>
      <div className="studio-grid">
        <div>
          <SceneEditor
            value={scene}
            onChange={(v) => {
              setScene(v);
              setNotice('');
            }}
            characters={characters}
            saved={scenes.data || []}
            onLoad={(s) => {
              setScene(s);
              setSceneId(s.id);
              setNotice('Scene loaded.');
            }}
          />
          <section className="director-note">
            <Clapperboard size={23} />
            <div>
              <h3>A little direction goes a long way.</h3>
              <p>
                Keep your first scene simple. Let personality come through in the pauses, glances
                and small reactions.
              </p>
            </div>
          </section>
        </div>
        <DialogueEditor
          value={script}
          onChange={(v) => {
            setScript(v);
            setNotice('');
          }}
          characters={characters}
          saved={scripts.data || []}
          onLoad={(s) => {
            setScript(s);
            setScriptId(s.id);
            setNotice('Conversation loaded.');
          }}
        />
      </div>
      <section className="render-bar">
        <div>
          <span className="eyebrow">READY WHEN YOU ARE</span>
          <h3>Make the moment.</h3>
        </div>
        <div className="output-field">
          <span>Output</span>
          <div className="output-options" role="group" aria-label="Output">
            <button
              type="button"
              aria-pressed={kind === 'storyboard'}
              className={kind === 'storyboard' ? 'active' : ''}
              onClick={() => setKind('storyboard')}
            >
              Silent storyboard
            </button>
            <UnavailableFeature reason={capabilities.animationReason}>
              <button
                type="button"
                aria-pressed={kind === 'animated'}
                className={kind === 'animated' ? 'active' : ''}
                onClick={() => setKind('animated')}
              >
                Animated conversation
              </button>
            </UnavailableFeature>
          </div>
        </div>
        <label>
          Duration
          <select value={seconds} onChange={(e) => setSeconds(+e.target.value)}>
            <option value={10}>10 sec · test</option>
            <option value={60}>60 sec · demo</option>
          </select>
        </label>
        <button
          className="button secondary"
          onClick={() => save()}
          disabled={busy || !script.turns.every((t) => t.text.trim())}
        >
          <Save size={16} />
          {busy ? 'Saving…' : 'Save project'}
        </button>
        <UnavailableFeature
          reason={
            kind === 'animated'
              ? capabilities.animationReason || capabilities.workerReason
              : capabilities.workerReason
          }
          className="render-action"
        >
          <button className="button primary" onClick={() => save(true)} disabled={busy || !ready}>
            {kind === 'storyboard' ? 'Create storyboard' : 'Render conversation'}
            <ArrowRight size={17} />
          </button>
        </UnavailableFeature>
      </section>
      <p className="render-disclaimer">
        {kind === 'storyboard'
          ? 'Storyboards show the scene only, without speech or animation. Animated conversations are unavailable in this MVP until enabled.'
          : status.data?.capabilities.animated_video
            ? 'Animated renders use your connected GPU services and require two authorized voice references.'
            : 'Animated rendering needs Chatterbox and InfiniteTalk GPU services. Configure them in your Hugging Face deployment.'}
      </p>
      {editing && <CharacterEditor character={editing} onClose={() => setEditing(undefined)} />}
    </>
  );
}
