import { useState } from 'react';
import { DEMO_IMAGE_ID } from '../../shared/api/demo';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Server, Check, RefreshCw, ShieldCheck } from 'lucide-react';
import { api } from '../../shared/api/client';
import { ErrorNotice, External, PageTitle } from '../../shared/components/ui';
export function SettingsPage() {
  const status = useQuery({ queryKey: ['system'], queryFn: api.status }),
    assets = useQuery({ queryKey: ['assets'], queryFn: api.assets }),
    client = useQueryClient();
  const [checks, setChecks] = useState<Record<string, { ready: boolean; message: string }>>(),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>();
  async function check() {
    setBusy(true);
    try {
      setChecks(await api.check());
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  async function revoke(id: string) {
    if (
      !window.confirm(
        'Revoke this asset? It will no longer be available for rendering or download.',
      )
    )
      return;
    try {
      await api.revoke(id);
      await client.invalidateQueries({ queryKey: ['assets'] });
    } catch (e) {
      setError(e);
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="BEHIND THE SCENES"
        title="Settings"
        description="Manage connections and uploaded assets."
        action={
          <button className="button secondary" disabled={busy} onClick={check}>
            <RefreshCw size={16} />
            {busy ? 'Checking…' : 'Check connections'}
          </button>
        }
      />
      <ErrorNotice error={error || status.error} />
      <div className="provider-grid">
        {Object.entries(status.data?.providers || {}).map(([key, p]) => (
          <section className="panel provider" key={key}>
            <Server size={24} />
            <span className="eyebrow">{key}</span>
            <h2>{p.name}</h2>
            <span className={`pill ${checks?.[key]?.ready ? 'success' : ''}`}>
              {checks?.[key]?.message ||
                (p.configured ? 'Configured · not verified' : 'Not configured')}
            </span>
            {!(key === 'dialogue'
              ? status.data?.capabilities.ai_dialogue
              : status.data?.capabilities.animated_video) && (
              <p className="hint">
                Disabled for this MVP. Connection checks do not enable the feature.
              </p>
            )}
            <p>
              {key === 'dialogue'
                ? 'Creates editable dialogue drafts. Scripted mode works without it.'
                : key === 'speech'
                  ? 'Synthesizes speech using your authorized voice references.'
                  : 'Animates both characters from a shared image and two audio tracks.'}
            </p>
          </section>
        ))}
      </div>
      <section className="panel settings-panel">
        <h2>Hugging Face deployment</h2>
        <p>
          Set <code>SPEECH_URL</code>, <code>VIDEO_URL</code>, <code>OLLAMA_URL</code> and{' '}
          <code>PROVIDER_TOKEN</code> in Space variables and secrets. Credentials never enter the
          browser.
        </p>
        <p>
          Worker: <strong>{status.data?.worker ? 'Heartbeat received' : 'No heartbeat yet'}</strong>
          . Start the separate worker with the API.
        </p>
        <External href="https://huggingface.co/docs/hub/spaces-sdks-docker">
          Docker Spaces documentation
        </External>
      </section>
      <section className="panel settings-panel">
        <h2>
          <ShieldCheck size={21} />
          Demo assets
        </h2>
        <p>
          This MVP uses the included fictional scene. Image uploads and character editing are
          disabled.
        </p>
        {assets.data?.length ? (
          <div className="asset-list">
            {assets.data.map((a) => (
              <div className="asset-row" key={a.id}>
                <div>
                  <strong>{a.name}</strong>
                  <small>
                    {a.kind} · {a.rights} · {a.rights_note}
                  </small>
                </div>
                {a.id !== DEMO_IMAGE_ID && (
                  <button className="button text" onClick={() => revoke(a.id)}>
                    Revoke
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">Your uploaded assets will appear here.</p>
        )}
      </section>
      <section className="panel settings-panel">
        <h2>What to review</h2>
        {status.data?.limitations.map((l) => (
          <p className="row" key={l}>
            <Check size={16} />
            {l}
          </p>
        ))}
      </section>
    </>
  );
}
