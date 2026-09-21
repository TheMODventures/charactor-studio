import { useState } from 'react';
import { assetUrl } from '../../shared/api/client';
import { DEMO_IMAGE_ID } from '../../shared/api/demo';

export function ScenePreview() {
  const [failed, setFailed] = useState(false);
  return (
    <section className="panel simple-scene fixed-scene">
      <div className="panel-header">
        <div>
          <span className="step">1</span>
          <h2>Your characters</h2>
        </div>
      </div>
      <div className="panel-content">
        <div className="scene-preview">
          {failed ? (
            <p className="fixed-image-error" role="alert">
              The demo image could not be loaded. Refresh once the backend is available.
            </p>
          ) : (
            <img
              src={assetUrl(DEMO_IMAGE_ID)}
              alt="R.Royale and Summer Breeze seated together in the demo scene"
              onError={() => setFailed(true)}
            />
          )}
        </div>
        <div className="fixed-cast-captions">
          <div>
            <strong>R.Royale</strong>
            <span>Calm, dry and thoughtful</span>
          </div>
          <div>
            <strong>Summer Breeze</strong>
            <span>Warm, lively and expressive</span>
          </div>
        </div>
      </div>
    </section>
  );
}
