# AI Character Creator — MVP Technical Plan

Engineering scope, limitations and estimates • USD • Planning assumptions, not a binding quote

**1. What is the smallest credible MVP?**
Two seated characters, one environment, one camera, limited upper-body gestures and a 55–65-second export.  
Include profile editing, both dialogue modes, audio preview and save/reload; defer live chat and arbitrary character creation.

**2. What should the first milestone prove?**
In week 1, make a 10-second shared-scene sample with distinct voices, lip-sync and a visible listener reaction.  
Obtain approval of faces, hair, voices and realism before scaling; cinematic photorealism is not assumed.

**3. What is the implementation architecture?**
Use a lightweight web editor, Python/FastAPI, SQLite, asset storage and one background rendering worker.  
Flow: saved profiles → approved script → separate voice tracks → measured timeline → facial/body animation → MP4.

**4. How is creator-written text protected?**
Store immutable spoken text separately from delivery cues; personality must never silently change scripted wording.  
Check rendered speech against the script using transcription plus human listening; regenerate misread or added words.

**5. How are duration and turn-taking controlled?**
Start with roughly 110–140 words, synthesize each turn separately, then measure actual audio durations.  
Adjust pauses and safe speaking rates; request creator edits if locked dialogue cannot fit naturally into 55–65 seconds.

**6. What does the speech-control model contain?**
Keep vocabulary and AAVE grammar preferences distinct from slang, pronunciation, cadence and situational code-switching.  
Validate a few presets with the creator or a paid dialect reviewer; arbitrary accent transfer is outside V1.

**7. What are the LLM and TTS limitations?**
GPT-4.1 mini may miss nuance; Eleven v3 needs retries for delivery; Cartesia Sonic 3 needs the same voice audition.  
Treat accent and emotion controls as tested preferences, not guarantees; unsupported controls must be visible. [OpenAI model] [ElevenLabs controls] [Cartesia SDK]

**8. What are the avatar and animation limitations?**
MetaHuman needs GPU rendering and visual polish; its audio solver handles faces, not complete body performance. [MetaHuman animation]  
Audio2Face needs rig mapping and separate body control; HeyGen must prove precise two-person reactions before adoption. [NVIDIA animation] [HeyGen guide]

**9. How are listening and speaking motions combined?**
Route each voice only to its own facial solver; layer gaze, eyebrows and body gestures on separate timeline tracks.  
Blend curated listening clips with idle motion, avoiding speech-like mouth movement and abrupt gesture transitions.

**10. What exactly is persisted?**
Save a versioned character ID, asset/rig references, voice/model mapping, style rules, gesture ranges and rights metadata.  
Save approved scripts, WAV files, animation curves, timeline JSON and model versions; cached assets preserve accepted takes.

**11. How are providers replaceable in practice?**
Define DialogueProvider, SpeechProvider, FaceAnimator and SceneRenderer interfaces with capability checks and adapters.  
Use JSON, WAV and supported animation exports; engine-specific rigs and proprietary voices remain migration work.

**12. How is the 6–8-week estimate allocated?**
Week 1: feasibility; weeks 2–3: profiles/editor/dialogue/TTS; weeks 4–5: scene and animation integration.  
Weeks 6–8: creator review, polish, export checks and handover; allow 200–280 hours including basic animation work.

**13. What is the cost of one 60-second attempt?**
GPT-4.1 mini: ~$0.004 at 5k input/1k output tokens; Eleven v3: ~$0.10 per 1k spoken characters. [OpenAI model] [ElevenLabs pricing]  
Assume 0.25–1.5 GPU-hours at $2–$4/hour: ~$0.50–$6 compute; round to $1–$7 total pending the first render benchmark.

**14. What costs sit outside that per-render estimate?**
Allow $200–$500 for testing/hosting and $300–$1,000 for assets; developer polish is in the development estimate.  
MetaHuman is free below its stated $1m revenue threshold; check applicable engine seats and account minimums. [MetaHuman licensing]

**15. What would the optional HeyGen test cost?**
HeyGen quotes Avatar IV at about $4/minute for 1080p; a 10-second benchmark is approximately $0.67. [HeyGen guide]  
That tests visual quality only; it is not a quote or proof of support for the final two-character scene.

**16. What are the acceptance criteria?**
Deliver 55–65 seconds with consistent identities, distinct approved voices, accurate words and visible listener reactions.  
Verify lip-sync, profile reuse and both input modes; hand over source, editable scene, assets, setup notes and final MP4.

**Official references — checked 21 September 2026**

- [OpenAI model](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [ElevenLabs controls](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [Cartesia SDK](https://github.com/cartesia-ai/cartesia-python/blob/main/examples/examples.py)
- [MetaHuman animation](https://dev.epicgames.com/documentation/metahuman/audio-driven-animation)
- [NVIDIA animation](https://docs.nvidia.com/nim/digital-human/a2f-3d/latest/)
- [HeyGen guide](https://help.heygen.com/en/articles/11269603-heygen-avatar-iv-complete-guide)
- [ElevenLabs pricing](https://elevenlabs.io/pricing/api)
- [MetaHuman licensing](https://www.metahuman.com/license)
