import { NavLink, Routes, Route, Navigate, Link } from 'react-router-dom';
import {
  AudioLines,
  Clapperboard,
  UsersRound,
  Film,
  SlidersHorizontal,
  ArrowUpRight,
  CircleHelp,
} from 'lucide-react';
import { StudioPage } from '../features/generations/studio.page';
import { CharactersPage } from '../features/characters/characters.page';
import { RendersPage } from '../features/generations/renders.page';
import { SettingsPage } from '../features/settings/settings.page';
export function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" to="/">
          <span className="brand-icon">
            <AudioLines size={23} />
          </span>
          <span>
            character<span className="brand-light">studio</span>
          </span>
        </Link>
        <div className="workspace-label">YOUR WORKSPACE</div>
        <nav>
          {[
            { to: '/', label: 'Studio', icon: Clapperboard },
            { to: '/characters', label: 'Characters', icon: UsersRound },
            { to: '/renders', label: 'Renders', icon: Film },
            { to: '/settings', label: 'Settings', icon: SlidersHorizontal },
          ].map(({ to, label, icon: Icon }) => (
            <NavLink key={to} end={to === '/'} to={to}>
              <Icon size={19} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="studio-tip">
            <span className="pill">A GOOD FIRST TAKE</span>
            <h3>
              Start small.
              <br />
              Make it feel real.
            </h3>
            <p>Try a 10-second conversation before your full demo.</p>
            <Link to="/">
              Open the studio <ArrowUpRight size={15} />
            </Link>
          </div>
          <Link className="help-link" to="/settings">
            <CircleHelp size={17} />
            Setup & connections
          </Link>
          <div className="account">
            <span>CS</span>
            <div>
              <strong>Creator workspace</strong>
              <small>Original stories, your direction</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <span>
            Workspace <span className="slash">/</span> <strong>Character Studio</strong>
          </span>
          <span className="topbar-badge">
            <span className="dot" />
            Prototype workspace
          </span>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<StudioPage />} />
            <Route path="/characters" element={<CharactersPage />} />
            <Route path="/renders" element={<RendersPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <footer className="page-footer">
            <span>Made for original characters. Built around your voice.</span>
            <span>CHARACTER STUDIO / V1</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
