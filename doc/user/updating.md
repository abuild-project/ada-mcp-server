# Update or roll back

## Check for an update

When automatic checks are enabled, Ada MCP can report an available update
when you connect. To check right away, ask the Ada skill:

> Check now for a newer Ada MCP release. Tell me what's installed, what's
> available and what switching would change. Wait for me before installing.

Checking only looks for a release. To check from a terminal, use the
[release check command](../updating.md#check-status-or-change-the-policy).

## Apply an approved update

Approve the version you want after reviewing what needs to change. Keep the
previous runtime and its matching binding. If you use a native Ada entry in
Codex Desktop, keep a backup of that entry and fully quit and reopen Desktop
after switching. A compatible local skill or private Cloud plugin can usually
keep its installation while the runtime changes.

After switching, confirm the active version and
[run a real query](setup.md#run-your-first-query).
See the [manual update steps](../updating.md#ask-once-then-execute-the-approved-update)
for the download and setup procedure.

## Restore a working setup

- **Skill or Cloud plugin:** [Restore the previous runtime selection](../updating.md#restore-a-compatible-runtime-selection).
- **Codex Desktop tools:** [Restore the backed-up Ada entry](../updating.md#switch-native-clients-or-a-private-cloud-copy)
  and reopen Codex. If you also replaced the local skill, [restore it](../updating.md#switch-a-local-skill-without-losing-its-old-target).
- **Direct Docker:** [Use the previous helper and its matching binding](../updating.md#restore-the-direct-docker-runtime-and-binding).

For Cloud, use the retained runtime to recover. Restoring a plugin package
depends on the provider's available restore options.
Check the active version and run a query after rolling back.
