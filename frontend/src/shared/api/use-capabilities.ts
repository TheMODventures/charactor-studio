import { useQuery } from '@tanstack/react-query';
import { api } from './client';

export const unavailable = {
  dialogue:
    'AI dialogue drafting is not functional at the moment for this MVP. You can write and save dialogue manually.',
  animation:
    'Animated speech, lip-sync and gestures are not functional at the moment for this MVP. You can prepare a silent storyboard.',
  speechStyle:
    'Automatic speech-style controls are not functional at the moment for this MVP. Existing preferences are preserved.',
  performance:
    'Voice performance and gesture controls are not functional at the moment for this MVP. Existing settings are preserved.',
  voiceDirection:
    'Custom voice-direction instructions are not applied by the current speech model.',
  worker: 'Rendering is unavailable at the moment because the render worker is offline.',
  checking: 'Feature availability is being checked. Please try again shortly.',
  disconnected: 'Feature availability could not be checked. Reconnect to the backend to render.',
};

export function useCapabilities() {
  const status = useQuery({ queryKey: ['system'], queryFn: api.status, refetchInterval: 15000 });
  const dialogue = status.data?.capabilities.ai_dialogue === true;
  const animation = status.data?.capabilities.animated_video === true;
  const workerReason = status.isError
    ? unavailable.disconnected
    : status.isPending
      ? unavailable.checking
      : !status.data?.worker
        ? unavailable.worker
        : undefined;
  return {
    dialogue,
    animation,
    dialogueReason: dialogue ? undefined : unavailable.dialogue,
    animationReason: animation ? undefined : unavailable.animation,
    workerReason,
  };
}
