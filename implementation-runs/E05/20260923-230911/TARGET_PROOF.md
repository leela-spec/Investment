target_product: "yt-dlp 2026.08.19; FFmpeg 8.0.1-3ubuntu2; WhisperX 3.8.6; PySceneDetect 0.7.1"
expected_version: "Exact versions above in an isolated WSL2 Python 3.12.14 media environment"
official_interface_to_use: "yt-dlp CLI -> FFmpeg/ffprobe CLI -> WhisperX CLI with Silero VAD and alignment -> PySceneDetect CLI"
proof_action: "Process the IMF World Economic Outlook July 2026 Update: 3 Key Questions, Answered video into hashed source media, aligned timestamped transcript, and timestamp-linked scene frames"
independent_oracle: "Reconcile media duration with ffprobe; compare WhisperX output with the separately acquired source captions and burned-in caption frames; compare the headline projections with the IMF-authored video description"
facade_failure_example: "A local transcript or screenshots that can still be produced after deleting WhisperX or PySceneDetect, or a manifest that merely names those products without preserving their real outputs"

The initially selected January 2026 IMF clip was processed first but correctly
rejected as a transcript fixture: Silero VAD found no active speech because the
clip is music-only. The empty WhisperX output is retained in the external run
directory as negative evidence; it was not converted into invented text.
