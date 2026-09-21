import { useEffect, useId, useState, type ReactNode } from 'react';
import { Info } from 'lucide-react';

/** Keep unavailable controls visible, but block pointer and keyboard activation. */
export function UnavailableFeature({
  reason,
  children,
  className = '',
}: {
  reason?: string;
  children: ReactNode;
  className?: string;
}) {
  const [visible, setVisible] = useState(false);
  const descriptionId = useId();
  useEffect(() => {
    if (!visible) return;
    const timer = window.setTimeout(() => setVisible(false), 4500);
    return () => window.clearTimeout(timer);
  }, [visible]);
  return (
    <div
      className={`feature-gate ${reason ? 'is-unavailable' : ''} ${className}`}
      tabIndex={reason ? 0 : undefined}
      role={reason ? 'group' : undefined}
      aria-label={reason ? 'Unavailable MVP feature' : undefined}
      aria-disabled={reason ? true : undefined}
      aria-describedby={reason ? descriptionId : undefined}
      onMouseEnter={() => reason && setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => reason && setVisible(true)}
      onBlur={() => setVisible(false)}
      onClick={
        reason
          ? (event) => {
              event.preventDefault();
              setVisible(true);
            }
          : undefined
      }
      onKeyDown={
        reason
          ? (event) => {
              if (event.key === 'Escape') setVisible(false);
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                setVisible(true);
              }
            }
          : undefined
      }
    >
      <fieldset disabled={!!reason} className="feature-gate-controls">
        {children}
      </fieldset>
      {reason && (
        <span id={descriptionId} className="sr-only">
          {reason}
        </span>
      )}
      {reason && visible && (
        <div className="feature-toast" role="status" aria-live="polite">
          <Info size={19} />
          <div>
            <strong>Unavailable in this MVP</strong>
            <p>{reason}</p>
          </div>
        </div>
      )}
    </div>
  );
}
