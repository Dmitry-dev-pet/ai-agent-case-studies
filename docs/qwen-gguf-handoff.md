# One-time Qwen GGUF transfer via hosted GitHub Actions

This experiment uses a **GitHub-hosted Ubuntu** runner, not a Mac runner.

When a reviewed version of `.github/workflows/qwen-gguf-artifact.yml` is pushed to the default branch by the repository owner, the workflow downloads one fixed public Qwen GGUF from a resolved immutable Hugging Face revision, checks size/header, computes SHA-256, and uploads **only the GGUF and manifest** in a short-lived GitHub Actions artifact. No model weights enter Git history.

The operator uses ChatGPT's GitHub connector to download this named ZIP artifact to a file reference, then its Google Drive connector to store it privately in **ChatGPT-Local-LLM**. Verify the GGUF SHA-256 against the manifest after reading the Drive copy; only then trigger the fixed cleanup workflow by creating an owner issue titled `[qwen-artifact-consumed] ARTIFACT_ID` using the verified GitHub artifact's numeric ID.

Cleanup checks the artifact name, size, nonexpiration and main-branch source before deleting exactly that ID via GitHub's Actions REST API. Artifact retention is one day as a fallback. Already-accrued artifact storage usage cannot be reversed by deletion.

The model itself is loaded and run **only in the ephemeral ChatGPT CPU container**, not on GitHub, Mac, Cloudflare, Colab, or VPS.
