# AI Character Creator — Client Response

Proposed MVP • R.Royale and Summer Breeze • Two short answer lines per question

**1. What would the first prototype deliver?**
A small creator interface, two reusable characters, and one approximately 60-second, 1080p conversation.  
Both women share one seated scene; V1 produces an offline video with visible listener reactions.

**2. How would the characters differ?**
R.Royale starts calm, dry and controlled; Summer Breeze starts louder, animated and expressive.  
Each has a distinct approved voice and appearance, with editable personality and delivery settings.

**3. How would regional speech and AAVE work?**
Separate regional vocabulary, AAVE features, slang, pronunciation, cadence and code-switching from identity.  
V1 offers a few creator-approved presets and line overrides; African-American identity never selects a dialect.

**4. Can creators write the exact dialogue?**
Yes: scripted mode locks the words and applies saved voice and performance settings without rewriting.  
Generated mode creates an editable draft; creators approve it before speech and video generation.

**5. Which LLM would you use?**
OpenAI GPT-4.1 mini would draft structured dialogue and performance cues through a Python service. [OpenAI model]  
One scene planner maintains both personalities and continuity; a separate agent per character is unnecessary.

**6. Which voice technology would you test?**
ElevenLabs Eleven v3 is the first choice; Cartesia Sonic 3 is the comparison candidate. [ElevenLabs controls] [Cartesia SDK]  
Audition two licensed or designed voices; expressive control and regional pronunciation require listening tests.

**7. Which avatar/video technology would you use?**
Use two original MetaHuman characters rendered together in Unreal Engine, with persistent faces and bodies.  
Test HeyGen Avatar IV for a visual benchmark; its documented workflow does not establish our shared-scene needs. [HeyGen guide]

**8. Which lip-sync, facial and body technology would you use?**
Use MetaHuman Animator for audio-driven facial movement; test NVIDIA Audio2Face-3D as an alternative. [MetaHuman animation] [NVIDIA animation]  
Use Unreal Sequencer, Control Rig and licensed gesture clips for body motion, eye contact and listener reactions.

**9. How would both characters react naturally?**
A shared timeline drives separate speech, facial, gaze and body tracks while both characters remain visible.  
Schedule nods, smiles, breathing and restrained reactions around the dialogue; manually polish the final performance.

**10. What would you build versus integrate?**
Build the editor, saved profiles, dialogue modes, scene planning, provider adapters, job tracking and export flow.  
Integrate existing LLM, TTS, facial-animation and rendering tools; no custom foundation-model training is needed.

**11. How would character settings be saved and reused?**
Version profiles in a database: personality, vocabulary, pronunciation, cadence, voice mapping and gesture settings.  
Store face/body assets, hair, clothing, rigs, approved audio, scene files and consent records in asset storage.

**12. How would you avoid provider dependency?**
Keep dialogue, audio, animation and rendering behind separate interfaces with owned profiles and standard exports.  
Replacement remains possible, but matching a proprietary voice or retargeting a rig will require new validation.

**13. What are the consent safeguards?**
V1 uses original fictional designs and licensed or designed voices, with recorded provenance and AI disclosure.  
Real-person uploads stay disabled until verified authorization, permitted-use records and revocation controls exist.

**14. What is the estimated V1 timeline and development cost?**
Budget 6–8 weeks and 200–280 hours; at an illustrative $50/hour, development is $10,000–$14,000 USD.  
This planning estimate includes basic character setup and two review rounds; bespoke art and delayed approvals add scope.

**15. What are the expected third-party costs?**
Allow approximately $1–$7 per final-minute render attempt, plus $200–$500 for prototype testing and hosting.  
Reserve $300–$1,000 separately for licensed assets; subscription minimums and any required engine seats are extra.

**16. What relevant experience can be claimed?**
No verified portfolio was supplied, so this proposal makes no claim of previously shipped avatar projects.  
Before sending, add genuine project links and your exact contribution; present third-party animation work transparently.

**Official references — checked 21 September 2026**

- [OpenAI model](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [ElevenLabs controls](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [Cartesia SDK](https://github.com/cartesia-ai/cartesia-python/blob/main/examples/examples.py)
- [HeyGen guide](https://help.heygen.com/en/articles/11269603-heygen-avatar-iv-complete-guide)
- [MetaHuman animation](https://dev.epicgames.com/documentation/metahuman/audio-driven-animation)
- [NVIDIA animation](https://docs.nvidia.com/nim/digital-human/a2f-3d/latest/)
