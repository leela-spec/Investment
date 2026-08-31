# Target Proof — Module M01 (Hermes Baseline & Investment Profile)

```yaml
target_product: Hermes Agent
expected_version: v0.20.5 (2026.8.19)
official_interface_to_use: CLI (`hermes -p investment chat`), Profile Management (`hermes profile`), MCP CLI (`hermes mcp`)
proof_action: Run scoped Investment profile with persisted constraints, verify repo scope reading, and verify negative broker order refusal
independent_oracle: Verified Hermes CLI execution receipts and config file inspections
facade_failure_example: A mock Python script pretending to be Hermes or simulating chat responses without invoking the real runtime
```

## Runtime Evidence
- Executable: `/usr/local/bin/hermes`
- Version: `Hermes Agent v0.20.5 (2026.8.19) · upstream 1bbb6e5b · local 0159b51f`
- Provider: `opencode-free`
- Model: `muse-spark-1.2-contributor-free`
- Profile Directory: `/root/.hermes/profiles/investment`
- Primary Workspace: `/root/workspaces/Investment` on branch `ipos-modular-rebuild-2026-08-28`
