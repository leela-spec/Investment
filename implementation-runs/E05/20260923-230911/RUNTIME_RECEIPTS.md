# E05 runtime receipts

This is a reconstructed execution record from the live run. Exact product
versions, inputs, outputs, and exit results are retained, but the original full
stdout/stderr stream was not captured verbatim. That limitation remains an
explicit audit gap.

## Environment

```text
WSL2 Ubuntu
Python 3.12.14
yt-dlp 2026.08.19
ffmpeg 8.0.1-3ubuntu2
whisperx 3.8.6
PySceneDetect 0.7.1
```

## Acquisition

```powershell
.venv/bin/yt-dlp 'https://www.youtube.com/watch?v=vzZpKJlpqKo' \
  --write-info-json --write-description --write-thumbnail \
  --merge-output-format mkv -o 'current/source.%(ext)s'
```

Result: exit 0; video format 399 plus audio format 251-20 merged to
`current/source.mkv`. The source, info JSON, description, and thumbnail hashes
are recorded in `RESEARCH_ARTIFACT.yaml`.

## Audio and compatibility proxy

```powershell
ffmpeg -y -i current/source.mkv -vn -ac 1 -ar 16000 \
  -c:a pcm_s16le current/audio.wav
ffmpeg -v error -i current/audio.wav -f null -
ffmpeg -y -i current/source.mkv -map 0:v:0 -an -c:v libx264 \
  -preset fast -crf 16 -pix_fmt yuv420p current/analysis-proxy.mp4
```

Result: all commands exited 0. The extracted WAV decodes without errors. The
proxy was required after the PySceneDetect/OpenCV path failed to read the AV1
source frames.

## Transcription and alignment

```powershell
.venv/bin/whisperx current/audio.wav --model small.en --language en \
  --device cpu --compute_type int8 --batch_size 4 --vad_method silero \
  --output_dir current/transcript --output_format all \
  --segment_resolution sentence --print_progress True --threads 8 \
  --hotwords 'International Monetary Fund, IMF, global growth, inflation, \
Middle East, artificial intelligence, AI, monetary policy, tariffs'
```

Result: exit 0. Runtime log explicitly reported `Performing voice activity
detection using Silero`, `Performing transcription`, and `Performing
alignment`. Output contains 11 segments and 234 word alignments.

## Scene extraction

```powershell
.venv/bin/scenedetect -i current/analysis-proxy.mp4 -o current/scenes \
  detect-content --threshold 10 list-scenes \
  save-images --num-images 3 --jpeg --quality 90
```

Result: exit 0. PySceneDetect reported 3,864 processed frames, 19 scenes, and
57 saved images. The native scene CSV and four reviewed frames are hashed in
the manifest.

## Product-removal/facade check

```powershell
env -i HOME=/tmp/ipos-e05-clean PATH=/usr/bin:/bin \
  whisperx current/audio.wav --model small.en
env -i HOME=/tmp/ipos-e05-clean PATH=/usr/bin:/bin \
  scenedetect -i current/analysis-proxy.mp4 detect-content
```

Result: both invocations failed with exit code 127 (`No such file or
directory`). The static files remain readable, but regeneration crosses the
real product boundary.
