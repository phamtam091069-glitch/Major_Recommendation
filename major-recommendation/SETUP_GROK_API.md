# ⚠️ GROK API - DEPRECATED

This file is kept for historical reference only.

## Status: GROK API KEY HAS BEEN REMOVED

The GROK API key and all related GROK API functionality has been removed from this project for security and maintenance reasons.

### What Changed:

- ❌ GROK_API_KEY removed from `.env`
- ❌ GROK API calls disabled in `utils/fallback_api.py`
- ❌ All GROK configuration deprecated

### Current API Support:

- ✅ Claude API (Anthropic) - Primary API
- ✅ Custom endpoint support (llm.chiasegpu.vn)

### Migration:

If you need fallback API support, use Claude API with retry logic instead. See `SETUP_CLAUDE_API.md` for details.
