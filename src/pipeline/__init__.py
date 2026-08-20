"""The archive of settled logic — one module per feature.

Nothing lands here until it has been built in the command center notebook, verified by eye,
and stopped changing shape (`AGENTS.md` §6). Modules take their values as arguments; none of
them read config, mount Drive, or reach the network on import, which is what lets `tests/`
run anywhere.
"""
