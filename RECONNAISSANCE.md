# RECONNAISSANCE.md
---

## FDE Day-One Questions

### Q1: Ingestion Path
**How does Meltano handle a `meltano run` command?**

- The journey starts in `cli.py` (the Click CLI entry point). The `run` command is routed through a maze of decorators and subcommands.
- Eventually, it lands in the `MeltanoRunner` or `Runner` class, which is responsible for orchestrating pipeline execution.
- The actual invocation of a Singer tap (the data ingestion logic) is buried under layers of plugin management, environment resolution, and dynamic imports.
- Expect to traverse: `cli.py` → `commands/run.py` → `core/runner.py` → `plugin/command.py` → `singer/runner.py`.
- The code is allergic to directness—expect indirection, context managers, and a healthy dose of dynamic class loading.

### Q2: Blast Radius
**If the Meltano.yml parser or the internal SQLAlchemy metadata schema changes, what breaks?**

- The `Meltano.yml` parser is the lifeblood of project configuration. Any change here will ripple through project initialization, plugin discovery, and environment resolution.
- The SQLAlchemy schema underpins the system DB. Changes here will break migrations, state management, and possibly orphan historical run data.
- In short: _everything_. The blast radius is total—expect breakage in project bootstrapping, plugin loading, and even CLI help output.

### Q3: Silent Debt
**Discrepancies between "Meltano 2.0/3.0" docs and legacy code?**

- The docs talk a big game about "Plugin Definitions" and a clean, modern architecture.
- In reality, `discovery.yml` and legacy plugin logic still lurk in the codebase, especially around plugin discovery and environment variable handling.
- There are vestigial code paths for old-style plugin definitions, and the migration to the new model is... incomplete.
- Watch for: code that references both `discovery.yml` and new plugin classes, and logic that tries to bridge the gap (usually with TODOs and warnings).

### Q4: Hidden Architecture
**Where is state actually stored?**

- State is split between the `system_db` (SQLAlchemy) and incremental state bookmarks (often JSON blobs or files).
- The logic for managing state is scattered: look in `core/state.py`, `system/db.py`, and various plugin-specific state handlers.
- The "real" state is a Frankenstein: part database, part file, part in-memory, and part "hope for the best."

### Q5: Dead Wood
**Deprecated features with low coverage/activity?**

- Early UI components (e.g., the old web UI) are still present but clearly unloved.
- Legacy environment variable handling (pre-2.0) is scattered and poorly tested.
- Some plugin types and discovery logic are marked as deprecated but not actually removed.
- The test suite skips or ignores these features—if they break, nobody will notice (or care).

---

## Difficulty Analysis

### Where Do Humans Get Lost?
- The inheritance tree for Plugin types is a labyrinth. Multiple base classes, mixins, and dynamic attributes make it nearly impossible to trace behavior without a graph.
- The abstraction layer between the CLI and the `Project` class is a black box. Data flows through context objects, dependency injectors, and global state.
- Tracing a setting from `.env` → config → plugin execution is a Herculean task. The flow is non-linear, with overrides, fallbacks, and magic environment resolution.

### Hardest Parts to Map Without a Graph
- Plugin instantiation and execution: The dynamic loading and registration of plugins is so abstracted that only a graph can reveal the true call paths.
- State management: The interplay between the system DB, state files, and in-memory state is opaque and scattered.
- Configuration propagation: Following a config value from source to sink (especially across legacy and new code) is nearly impossible without automated tooling.

---

_If you are reading this at 2:00 AM, good luck. The codebase is a living fossil—layered, inconsistent, and full of surprises. Bring coffee and a graph._