# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Python Backend (Main API)
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --extra dev

# Start development server
uv run python main.py  # Uses uvicorn internally

# Run tests
uv run pytest

# Run specific test file
uv run pytest app/video/test_service.py

# Linting and formatting
uv run ruff check .              # Check for linting issues
uv run ruff check . --fix        # Fix auto-fixable issues (preserves import order)
uv run ruff format .             # Format code (does not reorder imports)

# Type checking
uv run pyright .                 # Run type checking

# Combined check (recommended for CI)
uv run ruff check . && uv run ruff format --check . && uv run pyright .

# Pre-commit setup (one-time)
uv run pre-commit install

# Note: Pre-commit runs ruff but not pyright (due to venv dependencies)
# Always run pyright manually before pushing
```

## Architecture Overview

This is an **Auto-Lyricer** application that synchronizes lyrics with YouTube videos through automated transcription and alignment.

### Core Architecture Patterns

1. **Dependency Injection (Python Backend)**
   - Uses `dependency-injector` library
   - Each module has its own container in `container.py`
   - Main `AppContainer` in `app/container.py` wires all modules
   - Resources like DB connections are singletons

2. **Domain-Driven Design**
   - `/video` - YouTube video management
   - `/lyric` - Lyrics storage and retrieval
   - `/transcription` - Audio-to-text conversion
   - `/subtitle` - Synchronized subtitle generation
   - `/stt` - Speech-to-text processing pipeline

3. **Repository Pattern**
   - Model → Repository → Service → API layers
   - Repository handles data access
   - Service contains business logic
   - API handles HTTP concerns

4. **API Structure**
   - All endpoints prefixed with `/api/v1/`
   - FastAPI for async operations
   - Uses dataclasses for data models

### Key Technical Details

- **Database**: SQLAlchemy with aiosqlite for async operations
- **Video Processing**: yt-dlp for YouTube extraction, FFmpeg for audio processing
- **STT Pipeline**: Modular design supporting multiple providers (Runpod, etc.)

### Testing Approach

- Use `pytest` with `pytest-asyncio` for async tests
- Each module has `test_api.py`, `test_repository.py`, `test_service.py`
- Mock external dependencies using `unittest.mock`
- Database tests use in-memory SQLite

### Important Conventions

- All Python async functions should use `async def`
- Repository methods return DTOs
- Services handle business logic and validation
- Use dependency injection rather than global imports, because it has some problems with monkey patching.
- Data models use dataclasses for type safety and simplicity

### ⚠️ Critical: Import Order & Gevent Monkey Patching

**DO NOT reorder imports in this project!** This backend uses gevent's monkey patching which requires very specific import order:

1. **Gevent imports must come first** - The `monkey_patch.py` module must be imported before any other async libraries
2. **Import order is critical** - Libraries must be loaded in the correct sequence for monkey patching to work
3. **Ruff import sorting is disabled** - We've disabled `I001` (import order) rule in the linting configuration
4. **Manual import management** - Always preserve existing import order when editing files

If import order is disrupted, you may see errors like:
- `MonkeyPatchWarning: Monkey-patching ssl after ssl has already been imported`
- Async operations not working correctly
- Circular import issues

When adding new imports, place them appropriately within the existing structure rather than letting auto-formatters reorganize them.
