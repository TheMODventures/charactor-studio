import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, ArrowUpRight, Mic, Image } from 'lucide-react';
import { api } from '../../shared/api/client';
import type { Character } from '../../shared/api/types';
import { Avatar, Loading, ErrorNotice, PageTitle, Empty } from '../../shared/components/ui';
import { CharacterEditor } from './character-editor';
export function CharactersPage() {
  const query = useQuery({ queryKey: ['characters'], queryFn: api.characters });
  const [editing, setEditing] = useState<Character | null | undefined>();
  return (
    <>
      <PageTitle
        eyebrow="YOUR CAST"
        title="Characters with character."
        description="Distinct voices. Individual personalities. Always yours."
        action={
          <button className="button primary" onClick={() => setEditing(null)}>
            <Plus size={17} />
            New character
          </button>
        }
      />
      <ErrorNotice error={query.error} />
      {query.isLoading ? (
        <Loading />
      ) : (
        <div className="character-grid">
          {query.data?.map((c) => (
            <article className="character-card" key={c.id}>
              <div
                className="character-visual"
                style={{ background: `linear-gradient(145deg, ${c.color}77, ${c.color}22)` }}
              >
                <Avatar character={c} large />
                <span className="pill">{c.archived ? 'Archived' : 'Original character'}</span>
              </div>
              <div className="character-content">
                <div className="row between">
                  <h2>{c.name}</h2>
                  <button
                    className="icon-button"
                    aria-label={`Edit ${c.name}`}
                    onClick={() => setEditing(c)}
                  >
                    <ArrowUpRight size={20} />
                  </button>
                </div>
                <p>{c.description || 'Your next original character.'}</p>
                <div className="character-meta">
                  <span>
                    <Mic size={14} />
                    {c.voice_asset_id ? 'Voice saved' : 'Add voice'}
                  </span>
                  <span>
                    <Image size={14} />
                    {c.image_asset_id ? 'Image saved' : 'Add image'}
                  </span>
                  <span>v{c.version}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
      {query.data?.length === 0 && (
        <Empty title="Your cast starts here">Create your first character to get started.</Empty>
      )}
      {editing !== undefined && (
        <CharacterEditor character={editing || undefined} onClose={() => setEditing(undefined)} />
      )}
    </>
  );
}
