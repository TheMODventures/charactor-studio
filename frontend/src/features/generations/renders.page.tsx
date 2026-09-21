import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Download, RefreshCw, X, FileJson, CheckCircle2 } from 'lucide-react';
import { api, assetUrl } from '../../shared/api/client';
import type { Generation } from '../../shared/api/types';
import { Empty, ErrorNotice, Loading, PageTitle, Modal } from '../../shared/components/ui';
export function RendersPage() {
  const query = useQuery({ queryKey: ['generations'], queryFn: api.jobs, refetchInterval: 3000 }),
    client = useQueryClient();
  const [error, setError] = useState<unknown>(),
    [review, setReview] = useState<Generation>(),
    [checks, setChecks] = useState<Record<string, boolean | string>>({
      exact_words: false,
      consistent_identity: false,
      natural_reactions: false,
      lip_sync: false,
      notes: '',
    });
  async function action(fn: () => Promise<unknown>) {
    try {
      await fn();
      await client.invalidateQueries({ queryKey: ['generations'] });
      setError(null);
    } catch (e) {
      setError(e);
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="YOUR PRODUCTIONS"
        title="From conversation to creation."
        description="Follow each render, review the performance and keep the takes you love."
      />
      <ErrorNotice error={error || query.error} />
      {query.isLoading ? (
        <Loading />
      ) : !query.data?.length ? (
        <Empty title="Your first moment is waiting">
          Create a scene and save a conversation in the studio, then start a render.
        </Empty>
      ) : (
        <div className="render-list">
          {[...query.data].reverse().map((job) => (
            <article className="panel render-card" key={job.id}>
              <div className="render-thumb">
                {job.output_asset_id ? (
                  <video
                    aria-label={`Preview ${job.settings.conversation.title}`}
                    controls
                    preload="metadata"
                    src={assetUrl(job.output_asset_id)}
                  />
                ) : (
                  <img
                    src={assetUrl(job.settings.scene.image_asset_id)}
                    alt="Scene being rendered"
                  />
                )}
              </div>
              <div className="render-info">
                <div className="row between">
                  <span
                    className={`pill ${job.status === 'failed' ? 'danger' : job.status === 'completed' ? 'success' : ''}`}
                  >
                    {job.status}
                  </span>
                  <span className="small muted">{new Date(job.created_at).toLocaleString()}</span>
                </div>
                <h2>{job.settings.conversation.title}</h2>
                <p>
                  {job.settings.kind === 'storyboard'
                    ? 'Silent storyboard · no speech or animation'
                    : 'AI-generated conversation · review required'}{' '}
                  · {job.duration?.toFixed(1) || job.settings.target_seconds}s
                </p>
                <div
                  className="progress"
                  role="progressbar"
                  aria-label="Render progress"
                  aria-valuenow={job.progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <span style={{ width: `${job.progress}%` }} />
                </div>
                <p className="small">{job.stage}</p>
                {job.error && <div className="notice error">{job.error}</div>}
                <div className="row wrap">
                  {job.output_asset_id && (
                    <a className="button secondary" href={assetUrl(job.output_asset_id)} download>
                      <Download size={15} />
                      Download MP4
                    </a>
                  )}
                  <a
                    className="button text"
                    href={`/api/v1/generations/${job.id}/manifest`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <FileJson size={15} />
                    Saved inputs
                  </a>
                  {job.status === 'queued' && (
                    <button
                      className="button text"
                      onClick={() => action(() => api.cancel(job.id))}
                    >
                      <X size={15} />
                      Cancel
                    </button>
                  )}
                  {['failed', 'cancelled'].includes(job.status) && (
                    <button
                      className="button secondary"
                      onClick={() => action(() => api.retry(job.id))}
                    >
                      <RefreshCw size={15} />
                      Retry
                    </button>
                  )}
                  {job.status === 'completed' && job.settings.kind === 'animated' && (
                    <button
                      className="button primary"
                      onClick={() => {
                        setReview(job);
                        setChecks({
                          exact_words: false,
                          consistent_identity: false,
                          natural_reactions: false,
                          lip_sync: false,
                          notes: '',
                          ...job.review,
                        });
                      }}
                    >
                      <CheckCircle2 size={15} />
                      Review performance
                    </button>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
      {review && (
        <Modal title="Review the performance" onClose={() => setReview(undefined)}>
          <div className="modal-body">
            <p>Listen and watch the entire take before marking these checks.</p>
            {(
              [
                ['exact_words', 'The spoken words match the approved script'],
                ['consistent_identity', 'Faces, bodies and voices stay consistent'],
                ['natural_reactions', 'Listening reactions and gestures feel natural'],
                ['lip_sync', 'Lip movements match the correct speaker'],
              ] as const
            ).map(([key, label]) => (
              <label className="check review-check" key={key}>
                <input
                  type="checkbox"
                  checked={!!checks[key]}
                  onChange={(e) => setChecks({ ...checks, [key]: e.target.checked })}
                />
                {label}
              </label>
            ))}
            <label>
              Review notes
              <textarea
                value={String(checks.notes)}
                onChange={(e) => setChecks({ ...checks, notes: e.target.value })}
              />
            </label>
            <button
              className="button primary"
              onClick={() =>
                action(async () => {
                  await api.review(review.id, checks);
                  setReview(undefined);
                })
              }
            >
              Save review
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
