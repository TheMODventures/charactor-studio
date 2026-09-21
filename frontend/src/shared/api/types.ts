export interface Profile {
  personality: string;
  region: string;
  vocabulary: string;
  aave: string;
  slang: number;
  pronunciation: string;
  cadence: string;
  code_switching: string;
  expressiveness: number;
  pace: number;
  gestures: string;
  voice_notes: string;
}
export interface Character {
  id: string;
  name: string;
  description: string;
  color: string;
  profile: Profile;
  image_asset_id: string | null;
  voice_asset_id: string | null;
  archived: boolean;
  version: number;
  created_at: string;
}
export type CharacterInput = Omit<Character, 'id' | 'created_at' | 'version'>;
export interface Turn {
  character_id: string;
  text: string;
  direction: string;
  pause_after: number;
}
export interface Conversation {
  id: string;
  title: string;
  mode: 'scripted' | 'generated';
  turns: Turn[];
  approved: boolean;
  version: number;
}
export type ConversationInput = Omit<Conversation, 'id' | 'version'>;
export interface Scene {
  id: string;
  name: string;
  image_asset_id: string;
  character_ids: string[];
  prompt: string;
  approved: boolean;
  version: number;
}
export type SceneInput = Omit<Scene, 'id' | 'version'>;
export interface Asset {
  id: string;
  kind: string;
  name: string;
  url: string;
  rights: string;
  rights_note: string;
  revoked: boolean;
}
export interface Generation {
  id: string;
  status: string;
  stage: string;
  progress: number;
  conversation_id: string;
  scene_id: string;
  created_at: string;
  settings: {
    kind: 'storyboard' | 'animated';
    target_seconds: number;
    conversation: Conversation;
    scene: Scene;
    characters: Character[];
  };
  error: string | null;
  output_asset_id: string | null;
  duration: number | null;
  review: Record<string, boolean | string>;
}
export interface SystemStatus {
  worker: boolean;
  providers: Record<string, { name: string; configured: boolean }>;
  capabilities: { animated_video: boolean };
  limitations: string[];
}
