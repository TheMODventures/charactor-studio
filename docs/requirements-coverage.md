# MVP acceptance coverage

| Client requirement | Implemented application support | Remaining acceptance evidence |
| --- | --- | --- |
| Two original women with different personalities | Seed profiles, editable traits and versioning | Creator approves final appearances/voices |
| Save faces, bodies and voices | Image/scene assets, voice reference and generation snapshots | No editable 3D body rig; body appearance lives in scene imagery |
| Exact creator-written dialogue | Script editor and immutable render snapshot | Listen to TTS to confirm spoken fidelity |
| AI-generated dialogue | Qwen/Ollama provider and editable draft | Live model service test |
| Region, AAVE, slang, cadence, code-switching | Separate saved controls and draft context | Acoustic range and cultural authenticity review |
| Two people in one scene | Shared-image assignment and multi-person InfiniteTalk adapter | GPU speaker/face mapping and listener reactions |
| Lip-sync, facial movement, gestures | Audio-conditioned inference and performance prompt | Full GPU output review; no precision gesture timeline guarantee |
| Approximately 60 seconds | Target duration, measured audio and ±5-second constraint | Render and approve final take |
| Reusable/provider-independent architecture | Layers, protocols, adapters and saved input manifests | Replacing a voice provider requires a new voice audition |
| Consent | Rights metadata, attestation, revoke; no real-person face workflow | Human authorization review, not automated verification |
| Frontend and backend integration | React/Vite UI, FastAPI endpoints and real workflow E2E | See remote test logs for executed results |

Do not mark the client MVP complete until the GPU acceptance test is passed. The
application can be delivered and reviewed independently of that external dependency.
