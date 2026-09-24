# E05 verification report

## Target

Turn a real analyst video into a source-grounded, timestamped transcript and
visual-evidence package using yt-dlp, FFmpeg, WhisperX, and PySceneDetect.

## Result

PASS WITH AUDIT GAPS for the representative July 2026 IMF briefing. The run
produced a hashed 128.948-second source, clean 16 kHz analysis audio, 11
timestamped transcript segments with 234 aligned words, 19 product-detected
scenes, and four reviewed timestamp-linked evidence frames.

## Product-boundary evidence

- yt-dlp acquired the real IMF source, metadata, description, thumbnail, and
  source captions.
- FFmpeg extracted audio and produced the H.264 analysis proxy required because
  the installed PySceneDetect/OpenCV backend could not decode the original AV1.
- WhisperX ran Silero VAD, transcription, and phoneme alignment. Alignment was
  not disabled.
- PySceneDetect's ContentDetector generated the scene boundaries and candidate
  frames; IPOS did not implement a substitute shot detector.

A clean-path regeneration check found neither WhisperX nor PySceneDetect and
both product invocations failed with exit code 127. Existing static artifacts
remain readable without the products, but they cannot prove or regenerate the
product-native transcript/alignment and scene outputs by themselves.

## Independent checks

- ffprobe reports 128.948 seconds; aligned speech spans 5.794–123.642 seconds.
- The extracted WAV decodes with zero FFmpeg errors.
- The headline 3.0%/3.4% growth projections agree across the IMF-authored video
  description, WhisperX output, YouTube automatic captions, and a visually
  inspected burned-in caption frame. The automatic captions are comparison
  evidence, not publisher-supplied subtitles or numerical authority.
- All selected frames were visually inspected at original resolution.
- The January 2026 candidate was rejected after real VAD found no speech; its
  empty transcript was retained rather than misrepresented as a successful run.

## Quality boundary

The functional fixture is usable for reviewed evidence extraction, not
automatically fact-verified. Three visible ASR errors are called out in
`RESEARCH_ARTIFACT.yaml`; the raw transcript is content-addressed but writable.
E06 may create reviewed claims and corrections while preserving the raw quote,
timestamp, and source hash.

## Remaining gap

Original command output was observed live but was not preserved verbatim; the
execution record is reconstructed in `RUNTIME_RECEIPTS.md`. The content hashes
detect changes, but the external files are writable and therefore are not
filesystem-immutable. M08-T04 same-source deduplication and M08-T05 private or
unsupported-source routing remain unproven.

This proves one representative end-to-end run, not a scheduled batch service.
Automation belongs after the research and portfolio workflow is proven. The
next value target is E06: structured claim extraction from this media artifact
set with exact content hashes and provenance.
