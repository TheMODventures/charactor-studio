import { useState } from 'react';
import { Upload } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorNotice } from './ui';
import type { Asset } from '../api/types';
export function AssetUpload({
  kind,
  onUploaded,
}: {
  kind: 'image' | 'voice';
  onUploaded: (asset: Asset) => void;
}) {
  const [file, setFile] = useState<File | null>(null),
    [rights, setRights] = useState('original'),
    [note, setNote] = useState(''),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>();
  const query = useQueryClient();
  async function upload() {
    if (!file) return;
    setBusy(true);
    setError(null);
    const form = new FormData();
    form.append('file', file);
    form.append('kind', kind);
    form.append('rights', rights);
    form.append('rights_note', note);
    form.append('consent', String(consent));
    try {
      const asset = await api.upload(form);
      await query.invalidateQueries({ queryKey: ['assets'] });
      onUploaded(asset);
      setFile(null);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="upload-box">
      <label className="file-label">
        <Upload size={20} />
        <span>
          {file
            ? file.name
            : kind === 'image'
              ? 'Choose a fictional character / scene image'
              : 'Choose a voice reference'}
          <small>
            {kind === 'image'
              ? 'PNG or JPEG · up to 20 MB'
              : '16-bit PCM WAV · 3–30 seconds · up to 20 MB'}
          </small>
        </span>
        <input
          aria-label={`Upload ${kind}`}
          type="file"
          accept={kind === 'image' ? 'image/png,image/jpeg' : '.wav'}
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
      </label>
      {file && (
        <div className="upload-details">
          <label>
            Rights
            <select value={rights} onChange={(e) => setRights(e.target.value)}>
              <option value="original">Original / creator owned</option>
              <option value="licensed">Licensed for this use</option>
              {kind === 'voice' && <option value="authorized">Explicitly authorized voice</option>}
            </select>
          </label>
          <label>
            Ownership or authorization details
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Who owns this asset and what use is allowed?"
            />
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
            />
            {kind === 'image'
              ? 'I have rights to use this fictional image. It does not depict a real person.'
              : 'I have explicit rights to synthesize speech using this voice.'}
          </label>
          <button
            type="button"
            className="button secondary"
            disabled={!consent || note.trim().length < 5 || busy}
            onClick={upload}
          >
            {busy ? 'Uploading…' : 'Upload asset'}
          </button>
        </div>
      )}
      <ErrorNotice error={error} />
    </div>
  );
}
