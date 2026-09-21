import type {
  Asset,
  Character,
  CharacterInput,
  Conversation,
  ConversationInput,
  Scene,
  SceneInput,
  Generation,
  SystemStatus,
  Turn,
} from './types';
const root = '/api/v1';
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(root + path, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message =
        typeof body.detail === 'string'
          ? body.detail
          : body.detail?.map((e: { msg: string }) => e.msg).join('; ') || message;
    } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
const body = (value: unknown) => ({ method: 'POST', body: JSON.stringify(value) });
export const assetUrl = (id: string) => `${root}/assets/${encodeURIComponent(id)}/file`;
export const api = {
  characters: () => request<Character[]>('/characters'),
  saveCharacter: (data: CharacterInput, id?: string) =>
    request<Character>(`/characters${id ? '/' + id : ''}`, {
      ...body(data),
      method: id ? 'PUT' : 'POST',
    }),
  conversations: () => request<Conversation[]>('/conversations'),
  saveConversation: (data: ConversationInput, id?: string) =>
    request<Conversation>(`/conversations${id ? '/' + id : ''}`, {
      ...body(data),
      method: id ? 'PUT' : 'POST',
    }),
  draft: (topic: string, character_ids: string[]) =>
    request<{ turns: Turn[] }>('/conversations/draft', body({ topic, character_ids })),
  scenes: () => request<Scene[]>('/scenes'),
  saveScene: (data: SceneInput, id?: string) =>
    request<Scene>(`/scenes${id ? '/' + id : ''}`, { ...body(data), method: id ? 'PUT' : 'POST' }),
  assets: () => request<Asset[]>('/assets'),
  upload: (form: FormData) => request<Asset>('/assets', { method: 'POST', body: form }),
  revoke: (id: string) => request(`/assets/${id}/revoke`, body({})),
  jobs: () => request<Generation[]>('/generations'),
  generate: (conversation_id: string, scene_id: string, kind: string, target_seconds: number) =>
    request<Generation>('/generations', body({ conversation_id, scene_id, kind, target_seconds })),
  cancel: (id: string) => request(`/generations/${id}/cancel`, body({})),
  retry: (id: string) => request(`/generations/${id}/retry`, body({})),
  review: (id: string, review: Record<string, boolean | string>) =>
    request(`/generations/${id}/review`, body(review)),
  status: () => request<SystemStatus>('/system/status'),
  check: () =>
    request<Record<string, { ready: boolean; message: string }>>('/system/check', body({})),
};
