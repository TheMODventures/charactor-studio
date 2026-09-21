import { ImagePlus, Check } from 'lucide-react';
import type { Character, SceneInput, Scene } from '../../shared/api/types';
import { assetUrl } from '../../shared/api/client';
import { AssetUpload } from '../../shared/components/asset-upload';
export function SceneEditor({
  value,
  onChange,
  characters,
  saved,
  onLoad,
}: {
  value: SceneInput;
  onChange: (v: SceneInput) => void;
  characters: Character[];
  saved: Scene[];
  onLoad: (s: Scene) => void;
}) {
  const update = (v: Partial<SceneInput>) => onChange({ ...value, ...v, approved: false });
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="step">01</span>
          <h2>Set the scene</h2>
        </div>
        {value.approved && (
          <span className="pill success">
            <Check size={12} />
            Approved
          </span>
        )}
      </div>
      <div className="scene-preview">
        {value.image_asset_id ? (
          <img src={assetUrl(value.image_asset_id)} alt="Shared scene preview" />
        ) : (
          <div className="scene-placeholder">
            <div className="scene-art">
              <span />
              <span />
              <i />
            </div>
            <ImagePlus size={25} />
            <h3>Two characters. One scene.</h3>
            <p>Add a shared image with both characters visible.</p>
          </div>
        )}
        <span className="frame-label">SHARED SCENE · 16:9 RECOMMENDED</span>
      </div>
      <div className="panel-content">
        <div className="field-row">
          <label>
            Scene name
            <input value={value.name} onChange={(e) => update({ name: e.target.value })} />
          </label>
          {saved.length > 0 && (
            <label>
              Open saved
              <select
                aria-label="Open saved scene"
                defaultValue=""
                onChange={(e) => {
                  const s = saved.find((s) => s.id === e.target.value);
                  if (s) onLoad(s);
                }}
              >
                <option value="">Choose a scene</option>
                {saved.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        <div className="field-row">
          {['Left character', 'Right character'].map((label, index) => (
            <label key={label}>
              {label}
              <select
                value={value.character_ids[index] || ''}
                onChange={(e) => {
                  const ids = [...value.character_ids];
                  ids[index] = e.target.value;
                  update({ character_ids: ids });
                }}
              >
                <option value="">Choose character</option>
                {characters.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>
        <AssetUpload kind="image" onUploaded={(a) => update({ image_asset_id: a.id })} />
        <p className="hint">
          Two separate portraits can be saved to character profiles. This renderer needs one
          composed scene image; it does not merge portraits automatically.
        </p>
        <label>
          Scene direction
          <textarea
            rows={2}
            value={value.prompt}
            onChange={(e) => update({ prompt: e.target.value })}
          />
        </label>
        <label className="check">
          <input
            type="checkbox"
            checked={value.approved}
            onChange={(e) => onChange({ ...value, approved: e.target.checked })}
          />
          Both fictional characters are visible and their left/right assignments are correct.
        </label>
      </div>
    </section>
  );
}
