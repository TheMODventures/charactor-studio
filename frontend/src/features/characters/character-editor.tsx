import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, assetUrl } from '../../shared/api/client';
import type { Character, CharacterInput, Profile } from '../../shared/api/types';
import { Modal, ErrorNotice } from '../../shared/components/ui';
import { AssetUpload } from '../../shared/components/asset-upload';
export const defaultProfile: Profile = {
  personality: '',
  region: 'Creator defined',
  vocabulary: '',
  aave: 'Creator defined; no automatic dialect',
  slang: 0,
  pronunciation: '',
  cadence: 'Natural',
  code_switching: 'Context dependent',
  expressiveness: 0.5,
  pace: 1,
  gestures: 'Subtle conversational gestures',
  voice_notes: '',
};
export function CharacterEditor({
  character,
  onClose,
}: {
  character?: Character;
  onClose: () => void;
}) {
  const [value, setValue] = useState<CharacterInput>(
    character
      ? { ...character, profile: { ...defaultProfile, ...character.profile } }
      : {
          name: '',
          description: '',
          color: '#b9ace8',
          profile: defaultProfile,
          image_asset_id: null,
          voice_asset_id: null,
          archived: false,
        },
  );
  const [tab, setTab] = useState('Identity'),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>();
  const query = useQueryClient();
  const profile = (key: keyof Profile, v: string | number) =>
    setValue({ ...value, profile: { ...value.profile, [key]: v } });
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.saveCharacter(value, character?.id);
      await query.invalidateQueries({ queryKey: ['characters'] });
      onClose();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title={character ? 'Edit character' : 'Create a character'} onClose={onClose}>
      <form onSubmit={save}>
        <div className="segmented">
          {['Identity', 'Speech style', 'Performance', 'Assets'].map((t) => (
            <button
              type="button"
              className={tab === t ? 'active' : ''}
              key={t}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <div className="modal-body">
          {tab === 'Identity' && (
            <>
              <div className="field-row">
                <label>
                  Name
                  <input
                    required
                    maxLength={120}
                    value={value.name}
                    onChange={(e) => setValue({ ...value, name: e.target.value })}
                  />
                </label>
                <label className="color-field">
                  Accent
                  <input
                    type="color"
                    value={value.color}
                    onChange={(e) => setValue({ ...value, color: e.target.value })}
                  />
                </label>
              </div>
              <label>
                Short description
                <input
                  value={value.description}
                  onChange={(e) => setValue({ ...value, description: e.target.value })}
                />
              </label>
              <label>
                Personality
                <textarea
                  rows={5}
                  value={value.profile.personality}
                  onChange={(e) => profile('personality', e.target.value)}
                  placeholder="Their point of view, humor, interests and how they relate to others…"
                />
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={value.archived}
                  onChange={(e) => setValue({ ...value, archived: e.target.checked })}
                />
                Archive character
              </label>
            </>
          )}
          {tab === 'Speech style' && (
            <>
              <p className="hint">
                Speech preferences belong to the character, not their ethnicity. Dialect controls
                require listening review.
              </p>
              {(
                [
                  ['region', 'Regional influence'],
                  ['vocabulary', 'Preferred vocabulary'],
                  ['aave', 'AAVE preferences'],
                  ['pronunciation', 'Pronunciation notes'],
                  ['cadence', 'Cadence'],
                  ['code_switching', 'Code-switching'],
                ] as const
              ).map(([k, label]) => (
                <label key={k}>
                  {label}
                  <input value={value.profile[k]} onChange={(e) => profile(k, e.target.value)} />
                </label>
              ))}
              <label>
                Slang preference <span className="range-value">{value.profile.slang}%</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value.profile.slang}
                  onChange={(e) => profile('slang', +e.target.value)}
                />
              </label>
            </>
          )}
          {tab === 'Performance' && (
            <>
              <label>
                Expressiveness{' '}
                <span className="range-value">
                  {Math.round(value.profile.expressiveness * 100)}%
                </span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={value.profile.expressiveness}
                  onChange={(e) => profile('expressiveness', +e.target.value)}
                />
              </label>
              <label>
                Speaking pace <span className="range-value">{value.profile.pace.toFixed(2)}×</span>
                <input
                  type="range"
                  min="0.8"
                  max="1.2"
                  step="0.05"
                  value={value.profile.pace}
                  onChange={(e) => profile('pace', +e.target.value)}
                />
              </label>
              <label>
                Gestures and listener reactions
                <textarea
                  value={value.profile.gestures}
                  onChange={(e) => profile('gestures', e.target.value)}
                />
              </label>
              <label>
                Voice direction
                <textarea
                  value={value.profile.voice_notes}
                  onChange={(e) => profile('voice_notes', e.target.value)}
                />
              </label>
              <p className="hint">
                Pace and expressiveness apply to speech. Gesture prompts guide video generation;
                exact motion and pronunciation need review.
              </p>
            </>
          )}
          {tab === 'Assets' && (
            <>
              <h3>Character image</h3>
              {value.image_asset_id && (
                <img
                  className="asset-preview"
                  src={assetUrl(value.image_asset_id)}
                  alt="Saved character"
                />
              )}
              <AssetUpload
                kind="image"
                onUploaded={(a) => setValue({ ...value, image_asset_id: a.id })}
              />
              <h3>Authorized voice</h3>
              {value.voice_asset_id && <audio controls src={assetUrl(value.voice_asset_id)} />}
              <AssetUpload
                kind="voice"
                onUploaded={(a) => setValue({ ...value, voice_asset_id: a.id })}
              />
            </>
          )}
          <ErrorNotice error={error} />
        </div>
        <footer className="modal-footer">
          <button type="button" className="button secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="button primary" disabled={busy || !value.name.trim()}>
            {busy ? 'Saving…' : 'Save character'}
          </button>
        </footer>
      </form>
    </Modal>
  );
}
