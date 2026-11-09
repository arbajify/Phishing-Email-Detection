# Phishing Detection and Prevention System

A real-time phishing detection platform made of a Next.js dashboard, an API gateway, a detection API, and three ML services (text, URL, visual), backed by PostgreSQL, MongoDB and Redis. Everything runs locally with Docker Compose.

## Services and ports

| Service | Port |
|---|---|
| Frontend (Next.js) | 3080 |
| API gateway | 3000 |
| Detection API | 3001 |
| NLP service | 8000 |
| URL service | 8001 |
| Visual service | 8002 |

## Quick start

1. Copy the environment file and set a strong `POSTGRES_PASSWORD` and `JWT_SECRET`:

   ```bash
   cp .env.example .env
   ```

2. Start the stack:

   ```bash
   docker compose up --build -d
   ```

3. Download the phishing text model (about 1.3 GB, not stored in Git):

   ```bash
   docker compose exec nlp-service python -c "from huggingface_hub import snapshot_download; snapshot_download('ealvaradob/bert-finetuned-phishing', local_dir='/app/models/phishing-detector', allow_patterns=['*.json','*.txt','*.bin'])"
   docker compose exec nlp-service sh -c "cd /app/models/phishing-detector && cp -L pytorch_model.bin pytorch_model.real && mv -f pytorch_model.real pytorch_model.bin"
   docker compose restart nlp-service
   ```

   The second command replaces a symlink with a real file so Docker builds can read it. On Windows Git Bash, put `MSYS_NO_PATHCONV=1` in front of each `docker compose exec` command.

4. Check that the services are healthy:

   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   ```

   `"models_loaded": true` on the NLP service means the text model loaded.

5. Open http://localhost:3080, go to **Settings**, and enter the API URL `http://localhost:3000` and an API key. A test key is seeded on first run (see `docs/DEPLOYMENT_RUNBOOK.md`). Replace it before any public deployment.

## Changes in this version

- Added the missing `src/models` modules for the NLP, URL and visual services (model loaders, reputation scorer, CNN loader, screenshot similarity).
- Fixed the API gateway route mounting and request-body forwarding.
- Fixed a `detection-api` crash in the latency middleware.
- The ensemble decision lets one very confident model (0.9 or higher) set the result.
- Added social-engineering rules for gift-card, wire-transfer, secrecy and reimbursement scams.
- Narrowed the `.gitignore` rules so model source code is tracked and only weight files are ignored.

## Security notes

- Never expose the database ports (5432, 6379, 27018) on a public server.
- Rotate the seeded test API key and the default secrets before deploying.
- Put the gateway behind HTTPS.

## Acknowledgements

Built on an earlier phishing detection project by Harshdeep Athawale, used and modified with the author's permission. The text model is `ealvaradob/bert-finetuned-phishing` from Hugging Face (Apache-2.0).

## License

MIT. See [LICENSE](LICENSE).
