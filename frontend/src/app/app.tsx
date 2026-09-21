import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { AudioLines } from 'lucide-react';
import { StudioPage } from '../features/generations/studio.page';

export function App() {
  return (
    <div className="simple-shell">
      <header className="simple-app-header">
        <div className="simple-app-nav">
          <Link className="simple-brand" to="/">
            <AudioLines size={23} />
            <span>Character Studio</span>
          </Link>
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<StudioPage />} />
          <Route path="/characters" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="simple-app-footer">Original fictional characters · MVP</footer>
    </div>
  );
}
