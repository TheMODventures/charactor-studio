from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED
import re

OUT = Path(__file__).parent
sources = {
 'OpenAI model': 'https://developers.openai.com/api/docs/models/gpt-4.1-mini',
 'ElevenLabs controls': 'https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices',
 'ElevenLabs pricing': 'https://elevenlabs.io/pricing/api',
 'MetaHuman animation': 'https://dev.epicgames.com/documentation/metahuman/audio-driven-animation',
 'MetaHuman licensing': 'https://www.metahuman.com/license',
 'NVIDIA animation': 'https://docs.nvidia.com/nim/digital-human/a2f-3d/latest/',
 'Cartesia SDK': 'https://github.com/cartesia-ai/cartesia-python/blob/main/examples/examples.py',
 'HeyGen guide': 'https://help.heygen.com/en/articles/11269603-heygen-avatar-iv-complete-guide',
}

client = [
('What would the first prototype deliver?',
 'A small creator interface, two reusable characters, and one approximately 60-second, 1080p conversation.',
 'Both women share one seated scene; V1 produces an offline video with visible listener reactions.'),
('How would the characters differ?',
 'R.Royale starts calm, dry and controlled; Summer Breeze starts louder, animated and expressive.',
 'Each has a distinct approved voice and appearance, with editable personality and delivery settings.'),
('How would regional speech and AAVE work?',
 'Separate regional vocabulary, AAVE features, slang, pronunciation, cadence and code-switching from identity.',
 'V1 offers a few creator-approved presets and line overrides; African-American identity never selects a dialect.'),
('Can creators write the exact dialogue?',
 'Yes: scripted mode locks the words and applies saved voice and performance settings without rewriting.',
 'Generated mode creates an editable draft; creators approve it before speech and video generation.'),
('Which LLM would you use?',
 'OpenAI GPT-4.1 mini would draft structured dialogue and performance cues through a Python service. [OpenAI model]',
 'One scene planner maintains both personalities and continuity; a separate agent per character is unnecessary.'),
('Which voice technology would you test?',
 'ElevenLabs Eleven v3 is the first choice; Cartesia Sonic 3 is the comparison candidate. [ElevenLabs controls] [Cartesia SDK]',
 'Audition two licensed or designed voices; expressive control and regional pronunciation require listening tests.'),
('Which avatar/video technology would you use?',
 'Use two original MetaHuman characters rendered together in Unreal Engine, with persistent faces and bodies.',
 'Test HeyGen Avatar IV for a visual benchmark; its documented workflow does not establish our shared-scene needs. [HeyGen guide]'),
('Which lip-sync, facial and body technology would you use?',
 'Use MetaHuman Animator for audio-driven facial movement; test NVIDIA Audio2Face-3D as an alternative. [MetaHuman animation] [NVIDIA animation]',
 'Use Unreal Sequencer, Control Rig and licensed gesture clips for body motion, eye contact and listener reactions.'),
('How would both characters react naturally?',
 'A shared timeline drives separate speech, facial, gaze and body tracks while both characters remain visible.',
 'Schedule nods, smiles, breathing and restrained reactions around the dialogue; manually polish the final performance.'),
('What would you build versus integrate?',
 'Build the editor, saved profiles, dialogue modes, scene planning, provider adapters, job tracking and export flow.',
 'Integrate existing LLM, TTS, facial-animation and rendering tools; no custom foundation-model training is needed.'),
('How would character settings be saved and reused?',
 'Version profiles in a database: personality, vocabulary, pronunciation, cadence, voice mapping and gesture settings.',
 'Store face/body assets, hair, clothing, rigs, approved audio, scene files and consent records in asset storage.'),
('How would you avoid provider dependency?',
 'Keep dialogue, audio, animation and rendering behind separate interfaces with owned profiles and standard exports.',
 'Replacement remains possible, but matching a proprietary voice or retargeting a rig will require new validation.'),
('What are the consent safeguards?',
 'V1 uses original fictional designs and licensed or designed voices, with recorded provenance and AI disclosure.',
 'Real-person uploads stay disabled until verified authorization, permitted-use records and revocation controls exist.'),
('What is the estimated V1 timeline and development cost?',
 'Budget 6–8 weeks and 200–280 hours; at an illustrative $50/hour, development is $10,000–$14,000 USD.',
 'This planning estimate includes basic character setup and two review rounds; bespoke art and delayed approvals add scope.'),
('What are the expected third-party costs?',
 'Allow approximately $1–$7 per final-minute render attempt, plus $200–$500 for prototype testing and hosting.',
 'Reserve $300–$1,000 separately for licensed assets; subscription minimums and any required engine seats are extra.'),
('What relevant experience can be claimed?',
 'No verified portfolio was supplied, so this proposal makes no claim of previously shipped avatar projects.',
 'Before sending, add genuine project links and your exact contribution; present third-party animation work transparently.'),
]

technical = [
('What is the smallest credible MVP?',
 'Two seated characters, one environment, one camera, limited upper-body gestures and a 55–65-second export.',
 'Include profile editing, both dialogue modes, audio preview and save/reload; defer live chat and arbitrary character creation.'),
('What should the first milestone prove?',
 'In week 1, make a 10-second shared-scene sample with distinct voices, lip-sync and a visible listener reaction.',
 'Obtain approval of faces, hair, voices and realism before scaling; cinematic photorealism is not assumed.'),
('What is the implementation architecture?',
 'Use a lightweight web editor, Python/FastAPI, SQLite, asset storage and one background rendering worker.',
 'Flow: saved profiles → approved script → separate voice tracks → measured timeline → facial/body animation → MP4.'),
('How is creator-written text protected?',
 'Store immutable spoken text separately from delivery cues; personality must never silently change scripted wording.',
 'Check rendered speech against the script using transcription plus human listening; regenerate misread or added words.'),
('How are duration and turn-taking controlled?',
 'Start with roughly 110–140 words, synthesize each turn separately, then measure actual audio durations.',
 'Adjust pauses and safe speaking rates; request creator edits if locked dialogue cannot fit naturally into 55–65 seconds.'),
('What does the speech-control model contain?',
 'Keep vocabulary and AAVE grammar preferences distinct from slang, pronunciation, cadence and situational code-switching.',
 'Validate a few presets with the creator or a paid dialect reviewer; arbitrary accent transfer is outside V1.'),
('What are the LLM and TTS limitations?',
 'GPT-4.1 mini may miss nuance; Eleven v3 needs retries for delivery; Cartesia Sonic 3 needs the same voice audition.',
 'Treat accent and emotion controls as tested preferences, not guarantees; unsupported controls must be visible. [OpenAI model] [ElevenLabs controls] [Cartesia SDK]'),
('What are the avatar and animation limitations?',
 'MetaHuman needs GPU rendering and visual polish; its audio solver handles faces, not complete body performance. [MetaHuman animation]',
 'Audio2Face needs rig mapping and separate body control; HeyGen must prove precise two-person reactions before adoption. [NVIDIA animation] [HeyGen guide]'),
('How are listening and speaking motions combined?',
 'Route each voice only to its own facial solver; layer gaze, eyebrows and body gestures on separate timeline tracks.',
 'Blend curated listening clips with idle motion, avoiding speech-like mouth movement and abrupt gesture transitions.'),
('What exactly is persisted?',
 'Save a versioned character ID, asset/rig references, voice/model mapping, style rules, gesture ranges and rights metadata.',
 'Save approved scripts, WAV files, animation curves, timeline JSON and model versions; cached assets preserve accepted takes.'),
('How are providers replaceable in practice?',
 'Define DialogueProvider, SpeechProvider, FaceAnimator and SceneRenderer interfaces with capability checks and adapters.',
 'Use JSON, WAV and supported animation exports; engine-specific rigs and proprietary voices remain migration work.'),
('How is the 6–8-week estimate allocated?',
 'Week 1: feasibility; weeks 2–3: profiles/editor/dialogue/TTS; weeks 4–5: scene and animation integration.',
 'Weeks 6–8: creator review, polish, export checks and handover; allow 200–280 hours including basic animation work.'),
('What is the cost of one 60-second attempt?',
 'GPT-4.1 mini: ~$0.004 at 5k input/1k output tokens; Eleven v3: ~$0.10 per 1k spoken characters. [OpenAI model] [ElevenLabs pricing]',
 'Assume 0.25–1.5 GPU-hours at $2–$4/hour: ~$0.50–$6 compute; round to $1–$7 total pending the first render benchmark.'),
('What costs sit outside that per-render estimate?',
 'Allow $200–$500 for testing/hosting and $300–$1,000 for assets; developer polish is in the development estimate.',
 'MetaHuman is free below its stated $1m revenue threshold; check applicable engine seats and account minimums. [MetaHuman licensing]'),
('What would the optional HeyGen test cost?',
 'HeyGen quotes Avatar IV at about $4/minute for 1080p; a 10-second benchmark is approximately $0.67. [HeyGen guide]',
 'That tests visual quality only; it is not a quote or proof of support for the final two-character scene.'),
('What are the acceptance criteria?',
 'Deliver 55–65 seconds with consistent identities, distinct approved voices, accurate words and visible listener reactions.',
 'Verify lip-sync, profile reuse and both input modes; hand over source, editable scene, assets, setup notes and final MP4.'),
]

def make_doc(stem, title, subtitle, entries):
    refs = []
    for _, a, b in entries:
        for key in re.findall(r'\[([^]]+)\]', a+' '+b):
            if key not in refs: refs.append(key)
    md = [f'# {title}', '', subtitle, '']
    paragraphs = []
    def paragraph(text, style=None, keep=False):
        props = (f'<w:pStyle w:val="{style}"/>' if style else '') + ('<w:keepNext/>' if keep else '')
        return f'<w:p><w:pPr>{props}</w:pPr><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    paragraphs += [paragraph(title, 'Title'), paragraph(subtitle, 'Subtitle')]
    for i, (q,a,b) in enumerate(entries, 1):
        md += [f'**{i}. {q}**', a+'  ', b, '']
        paragraphs += [paragraph(f'{i}. {q}', 'Heading2', True), paragraph(a, keep=True), paragraph(b)]
    md += ['**Official references — checked 21 September 2026**', '']
    paragraphs.append(paragraph('Official references — checked 21 September 2026', 'Heading2'))
    for key in refs:
        md.append(f'- [{key}]({sources[key]})')
        paragraphs.append(paragraph(f'{key}: {sources[key]}', 'Source'))
    (OUT/(stem+'.md')).write_text('\n'.join(md)+'\n')
    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(paragraphs)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850"/></w:sectPr></w:body></w:document>'
    styles = '''<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="20"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="65" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:color w:val="153C56"/><w:sz w:val="34"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:color w:val="666666"/><w:sz w:val="19"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="60"/></w:pPr><w:rPr><w:b/><w:color w:val="153C56"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Source"><w:name w:val="Source"/><w:rPr><w:sz w:val="16"/></w:rPr></w:style></w:styles>'''
    with ZipFile(OUT/(stem+'.docx'), 'w', ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/_rels/document.xml.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr('word/document.xml', document)
        z.writestr('word/styles.xml', styles)

make_doc('01_Client_Response', 'AI Character Creator — Client Response', 'Proposed MVP • R.Royale and Summer Breeze • Two short answer lines per question', client)
make_doc('02_MVP_Technical_Plan', 'AI Character Creator — MVP Technical Plan', 'Engineering scope, limitations and estimates • USD • Planning assumptions, not a binding quote', technical)

if __name__ == '__main__':
    import xml.etree.ElementTree as ET
    for file in OUT.glob('*.docx'):
        with ZipFile(file) as z:
            assert z.testzip() is None
            for name in z.namelist(): ET.fromstring(z.read(name))
        print(f'Validated: {file.name}')
