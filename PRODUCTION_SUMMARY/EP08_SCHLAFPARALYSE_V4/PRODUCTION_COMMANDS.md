# EP08 Production Commands

```bash
# once for the whole trilogy
git pull origin master
python3 tools/prepare_schlafparalyse_production_inputs.py

# source media
cd 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2
python3 download_schlafparalyse_assets.py
cd ../../..

# voice
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/voice/voice_batch_v4.json --execute
python3 tools/schlafparalyse_voice.py EP08 all
```
