import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowRight, Check, Save } from 'lucide-react';
import { api, assetUrl, request } from '../../shared/api/client';
import type { ConversationInput, Generation } from '../../shared/api/types';
import { useCapabilities } from '../../shared/api/use-capabilities';
import { UnavailableFeature } from '../../shared/components/unavailable-feature';
import { ErrorNotice, Loading } from '../../shared/components/ui';
import { ScenePreview } from '../scenes/scene-preview';
import { DEMO_SCENE_ID, DEMO_IMAGE_ID, DEMO_CHARACTER_IDS } from '../../shared/api/demo';
import { DialogueEditor } from '../conversations/dialogue-editor';

export function StudioPage() {
  const capabilities = useCapabilities();
  const chars = useQuery({ queryKey: ['characters'], queryFn: api.characters });
  const scripts = useQuery({ queryKey: ['conversations'], queryFn: api.conversations });
  const scenes = useQuery({ queryKey: ['scenes'], queryFn: api.scenes });
  const characters =
    chars.data?.filter((c) => !c.archived && DEMO_CHARACTER_IDS.some((id) => id === c.id)) || [];
  const scene = scenes.data?.find((s) => s.id === DEMO_SCENE_ID);
  const [script, setScript] = useState<ConversationInput>({
    title: 'My first conversation',
    mode: 'scripted',
    approved: false,
    turns: [
      { character_id: 'royale', text: '', direction: '', pause_after: 0.4 },
      { character_id: 'summer', text: '', direction: '', pause_after: 0.4 },
    ],
  });
  const [scriptId, setScriptId] = useState<string>();
  const [seconds, setSeconds] = useState(60);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  const [notice, setNotice] = useState('');
  const query = useQueryClient();
  const [jobId, setJobId] = useState<string>();
  const job = useQuery({
    queryKey: ['generation', jobId],
    queryFn: () => request<Generation>(`/generations/${jobId}`),
    enabled: !!jobId,
    refetchInterval: (query) =>
      ['completed', 'failed', 'cancelled'].includes(query.state.data?.status || '') ? false : 3000,
  });
  const cast = DEMO_CHARACTER_IDS.map((id) => characters.find((c) => c.id === id)).filter(
    (c) => c !== undefined,
  );
  const scriptValid =
    !!script.title.trim() &&
    script.turns.every((t) => t.text.trim() && characters.some((c) => c.id === t.character_id));
  const sceneValid = scene?.image_asset_id === DEMO_IMAGE_ID && cast.length === 2;
  const matchingSpeakers =
    new Set(script.turns.map((t) => t.character_id)).size === 2 &&
    script.turns.every((t) => DEMO_CHARACTER_IDS.some((id) => id === t.character_id));
  const ready = scriptValid && sceneValid && matchingSpeakers && script.approved && scene?.approved;
  const remaining = !sceneValid
    ? 'The demo scene is not available. Check the backend connection.'
    : !scriptValid
      ? 'Give your conversation a name and fill in each line. Aim for about 120–140 words for 60 seconds.'
      : !matchingSpeakers
        ? 'Give both characters at least one line.'
        : !script.approved
          ? 'Approve the dialogue to create your preview.'
          : '';

  async function save(kind?: 'storyboard' | 'animated') {
    if (
      busy ||
      !scriptValid ||
      (kind &&
        (!ready || capabilities.workerReason || (kind === 'animated' && !capabilities.animation)))
    )
      return;
    setBusy(true);
    setError(null);
    setNotice('');
    try {
      const conversation = await api.saveConversation(script, scriptId);
      setScriptId(conversation.id);
      await query.invalidateQueries({ queryKey: ['conversations'] });
      if (kind && scene) {
        const generation = await api.generate(conversation.id, DEMO_SCENE_ID, kind, seconds);
        setJobId(generation.id);
        setNotice('Conversation saved. Your preview is queued below.');
      } else setNotice('Conversation saved.');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  if (chars.isLoading || scenes.isLoading) return <Loading />;
  return (
    <div className="simple-studio">
      <header className="simple-heading">
        <h1>Create a conversation</h1>
        <p>Write a conversation for R.Royale and Summer Breeze.</p>
      </header>
      <ErrorNotice error={chars.error || scripts.error || scenes.error || error} />
      {notice && (
        <div className="notice success" role="status">
          <Check size={16} />
          {notice}
        </div>
      )}
      <ScenePreview />
      <DialogueEditor
        value={script}
        onChange={(v) => {
          setScript(v);
          setNotice('');
        }}
        characters={cast}
        saved={scripts.data || []}
        onLoad={(s) => {
          setScript(s);
          setScriptId(s.id);
        }}
      />
      <section className="panel simple-export">
        <div className="panel-header">
          <div>
            <span className="step">3</span>
            <h2>Save or create</h2>
          </div>
        </div>
        <div className="panel-content">
          <div className="simple-export-row">
            <label>
              Duration
              <select value={seconds} onChange={(e) => setSeconds(+e.target.value)}>
                <option value={10}>10 seconds</option>
                <option value={60}>60 seconds</option>
              </select>
            </label>
            <p>
              The storyboard is a silent scene preview.
              <br />
              {capabilities.animation
                ? 'Talking videos animate both portraits separately with speech and lip-sync.'
                : 'Speaking and lip-sync are not available yet.'}
            </p>
          </div>
          {remaining && <p className="next-step">{remaining}</p>}
          <div className="simple-actions">
            <button
              className="button secondary"
              onClick={() => save()}
              disabled={busy || !scriptValid}
            >
              <Save size={16} />
              {busy ? 'Saving…' : 'Save draft'}
            </button>
            <UnavailableFeature reason={capabilities.workerReason}>
              <button
                className="button primary"
                disabled={busy || !ready}
                onClick={() => save('storyboard')}
              >
                Create storyboard
                <ArrowRight size={16} />
              </button>
            </UnavailableFeature>
            <UnavailableFeature reason={capabilities.animationReason || capabilities.workerReason}>
              <button
                className="button secondary"
                disabled={busy || !ready}
                onClick={() => save('animated')}
              >
                Create talking video
              </button>
            </UnavailableFeature>
          </div>
        </div>
      </section>
      {jobId && (
        <section className="panel">
          <div className="panel-header">
            <h2>Your preview</h2>
          </div>
          <div className="panel-content">
            <ErrorNotice error={job.error} />
            {job.isLoading && <Loading />}
            {job.data && (
              <>
                <p role="status">
                  {job.data.status} · {job.data.stage}
                </p>
                <p className="small muted">
                  {job.data.settings.kind === 'storyboard'
                    ? 'Silent scene preview — no spoken dialogue or lip-sync.'
                    : 'Review the spoken dialogue and animation before sharing.'}
                </p>
                {job.data.error && (
                  <div className="notice error" role="alert">
                    {job.data.error}
                  </div>
                )}
                {job.data.output_asset_id && (
                  <>
                    <video
                      controls
                      preload="metadata"
                      aria-label="Your generated preview"
                      src={assetUrl(job.data.output_asset_id)}
                      style={{ width: '100%' }}
                    />
                    <a
                      className="button secondary"
                      href={assetUrl(job.data.output_asset_id)}
                      download
                    >
                      Download MP4
                    </a>
                  </>
                )}
              </>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
