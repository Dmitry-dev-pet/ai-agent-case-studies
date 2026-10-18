# Chunked Qwen GGUF transfer via GitHub-hosted Actions

Use **GitHub-hosted Ubuntu**, never the user's Mac. A reviewed change to `.github/workflows/qwen-gguf-artifact.yml` on main triggers a one-time download of `notschmee/Qwen3.5-0.8B-GGUF`, `Qwen3.5-0.8B-Q4_K_M.gguf`, at its immutable resolved commit. Verify GGUF header, size, SHA-256. Split the file into two 300-MB-or-less pieces because the ChatGPT GitHub plugin enforces a **512 MiB maximum per artifact download**. Each of two short-lived, uncompressed ZIP artifacts includes its chunk and a shared manifest with part checksums, full checksum, source revision and sizes.

The operator downloads each ZIP through the ChatGPT GitHub connector, passes each file reference directly to the Google Drive connector, and verifies Drive readback of both ZIPs. Inside the **ChatGPT CPU container**, unzip both, check the manifest and individual chunk SHA-256 digests, concatenate in order and validate full GGUF SHA-256. Store two ZIPs permanently on Google Drive unless a raw verified GGUF can be uploaded there directly.

The initial oversized artifact from the 2026-10-18 first attempt is intentionally not downloaded through the connector: it exceeds 512 MiB. Clean it and the two split artifacts after Drive copies are verified, using exactly one owner issue **per artifact**: `[qwen-artifact-clean] ARTIFACT_ID`. The cleanup workflow checks exact known artifact names, bounded sizes and main-branch provenance before deletion via GitHub API.

No weights in git, no secrets, no Drive credentials in a runner, no Mac, Colab, VPS or Cloudflare. Artifact retention: **one day**, no inference on GitHub. Deleting artifacts stops future storage accrual, not earlier measured GB-hours.
