# AGENTS.md — PlatformIO Core

## 1. Project Overview

PlatformIO Core is the Python-based command-line core of the
PlatformIO ecosystem.

It provides infrastructure for embedded development, including:

- Project management and configuration.
- Platform and package management.
- Build system orchestration.
- Framework and toolchain integration.
- Library management.
- Device discovery and upload.
- Debugging infrastructure.
- Integration with IDEs and external development tools.

PlatformIO Core supports a wide range of embedded platforms,
toolchains, frameworks, architectures and hardware devices.

All changes must consider the broader PlatformIO ecosystem
and preserve compatibility with existing integrations.

## 2. Core Development Principles

- Understand the existing implementation before proposing changes.
- Prefer minimal, focused and maintainable changes.
- Preserve backward compatibility whenever possible.
- Avoid unnecessary refactoring unrelated to the task.
- Follow established project architecture and coding conventions.
- Reuse existing abstractions and utilities instead of duplicating logic.
- Avoid introducing new dependencies without clear justification.
- Do not assume all users have the same operating system,
  toolchain or development environment.
- Do not introduce breaking changes without explicit approval.
- Prefer evidence from source code, tests and documentation
  over assumptions.

## 3. Architecture Awareness

Before modifying code:

1. Identify the relevant modules and their responsibilities.
2. Trace the execution flow from the public interface to
   the underlying implementation.
3. Identify dependencies and integration points.
4. Check whether affected functionality is used by other
   PlatformIO components.
5. Review existing tests and related implementations.
6. Identify potential backward compatibility implications.

Pay particular attention to changes affecting:

- Platform and package management.
- Build system and build orchestration.
- Framework and toolchain integration.
- Project configuration and `platformio.ini` processing.
- Library management.
- Device discovery and upload.
- Debugging infrastructure.
- CLI commands and public interfaces.
- IDE and external development tool integrations.

Do not assume that a module operates independently.

## 4. Official Documentation

The `docs/` directory contains the official PlatformIO
documentation and is maintained as a Git submodule.

Use this documentation as an important source of context
when investigating features, user-facing behavior, APIs,
configuration options and ecosystem integrations.

### Documentation guidelines

- Inspect relevant documentation before changing user-facing
  behavior or public interfaces.
- Use official documentation to understand intended behavior
  and user expectations.
- Cross-reference documentation with the current source code.
- Do not assume documented functionality is implemented
  in the current branch.
- Do not assume all documented functionality belongs
  to PlatformIO Core.
- Identify whether documented behavior is implemented in Core,
  PlatformIO IDE, a development platform, a framework or
  another ecosystem component.
- Treat source code and tests as authoritative evidence of
  current implementation behavior.
- When implementation changes affect documented behavior,
  identify the relevant documentation pages that may require
  updates.

### Git submodule handling

- Do not modify the documentation submodule unless the task
  explicitly requires documentation changes.
- Do not update the submodule reference as part of unrelated
  Core development work.
- Preserve the currently checked-out documentation revision.
- Before documentation changes, inspect the submodule's
  Git status and current revision.
- Keep documentation changes separate from Core source changes
  whenever practical.
- Never discard existing user changes in the submodule.

## 5. Python Development

- Follow the Python versions officially supported by the project.
- Follow existing formatting, naming and coding conventions.
- Prefer clear and readable implementations.
- Avoid unnecessary abstractions and excessive complexity.
- Handle exceptions explicitly and consistently.
- Avoid swallowing exceptions or silently ignoring failures.
- Be careful with filesystem operations and subprocess execution.
- Consider Windows, Linux and macOS compatibility.
- Avoid introducing dependencies unless necessary.

Do not upgrade dependencies or change Python compatibility
requirements as part of an unrelated task.

## 6. PlatformIO Ecosystem Compatibility

PlatformIO Core is an integration layer between users,
platform packages, frameworks, toolchains and development tools.

When implementing changes:

- Preserve compatibility with existing platform packages.
- Consider third-party platform integrations.
- Do not assume a particular framework or toolchain.
- Preserve existing package management behavior.
- Consider different versions of platforms and frameworks.
- Avoid hardcoding platform-specific behavior into generic code.
- Consider offline and restricted-network environments where relevant.
- Consider different hardware architectures and development hosts.

Changes to public APIs, configuration formats, package behavior
or CLI commands require particular care.

## 7. Security and Reliability

- Treat downloaded packages and third-party platform integrations
  as untrusted inputs.
- Validate external input where appropriate.
- Review subprocess execution and command construction.
- Avoid unsafe shell execution.
- Handle filesystem paths carefully.
- Do not expose credentials, tokens or sensitive information.
- Avoid introducing insecure defaults.
- Preserve existing security boundaries.
- Handle network failures, timeouts and interrupted operations
  consistently.

## 8. Testing Requirements

Tests are an essential part of every implementation.

Before changing code:

- Locate and understand relevant existing tests.
- Identify appropriate test coverage for the change.
- Reuse existing test fixtures and helpers.
- Understand the project's test execution conventions.

### Bug fixes

- Add a regression test reproducing the original problem.
- Verify that the test fails before applying the fix.
- Implement the smallest reasonable correction.
- Verify that the regression test passes.

### New functionality

- Add tests covering normal behavior.
- Cover relevant edge cases and error conditions.
- Consider backward compatibility.
- Test platform-specific behavior where applicable.

### Test execution

- Run the most relevant tests first.
- Run broader test suites when appropriate.
- Report tests that could not be executed and explain why.
- Never claim tests passed unless they were actually executed.
- Do not weaken or remove existing tests merely to make
  an implementation pass.

## 9. Documentation Development

Official PlatformIO documentation uses Sphinx and
reStructuredText (RST).

All documentation changes must follow the existing
documentation structure and conventions.

### Sphinx and RST guidelines

- Use reStructuredText (`.rst`) for documentation pages
  unless the existing documentation structure specifies otherwise.
- Follow existing Sphinx configuration and extensions.
- Follow existing heading, section and formatting conventions.
- Use valid RST directives and roles.
- Use Sphinx cross-references where appropriate.
- Prefer references to existing documentation pages
  instead of duplicating information.
- Maintain consistent terminology with the existing
  PlatformIO documentation.
- Preserve existing page hierarchy and navigation.
- Keep examples accurate and executable where practical.
- Use existing conventions for code blocks, notes, warnings
  and other admonitions.
- Ensure internal references and links remain valid.
- Avoid introducing new Sphinx extensions without justification.

### RST formatting

Follow existing project conventions for:

- Section heading adornments.
- Inline literals and code blocks.
- External links and internal references.
- Figures and images.
- Notes, warnings and important messages.
- Tables and lists.

For example, use existing Sphinx conventions such as:

- ``inline literals``
- ``.. code-block:: python``
- ``.. note::``
- ``.. warning::``
- ``:ref:`reference-label``

Do not introduce Markdown-specific syntax into RST files.

### Documentation validation

When changing documentation:

- Check RST syntax.
- Check internal references and cross-references.
- Build the documentation using the project's configured
  Sphinx environment when available.
- Resolve new warnings introduced by the changes.
- Do not modify unrelated generated documentation files.

Do not modify Sphinx configuration or dependencies
unless explicitly required by the task.

## 10. Implementation Workflow

For every non-trivial task:

1. Investigate the existing implementation.
2. Explain the current behavior.
3. Identify affected modules and potential side effects.
4. Review relevant documentation and tests.
5. Propose an implementation approach.
6. Discuss important trade-offs when necessary.
7. Agree on the design for architectural changes.
8. Implement focused changes.
9. Add or update tests.
10. Update documentation when necessary.
11. Run relevant tests and validation.
12. Review the final Git diff.

Do not modify source code before understanding the problem
and the intended behavior.

For architectural changes, agree on the design before implementation.

## 11. Code Review Expectations

When reviewing changes, look for:

- Functional correctness.
- Backward compatibility.
- Cross-platform compatibility.
- Regression risks.
- Error handling.
- Security implications.
- Performance implications.
- Test coverage.
- Documentation accuracy.
- Unnecessary complexity.
- Unrelated modifications.

Prioritize concrete problems over stylistic preferences.

Distinguish between actual defects and optional improvements.

## 12. Git and Change Management

- Keep changes focused on the requested task.
- Do not overwrite unrelated user modifications.
- Do not reset, revert or discard user changes without permission.
- Do not commit or push unless explicitly requested.
- Review `git status` before modifying files.
- Review `git diff` before considering implementation complete.
- Pay particular attention to Git submodule changes.
- Avoid accidentally committing submodule reference updates.
- Provide a concise summary of modifications and test results.

## 13. Agent Behavior

Act as an experienced Python engineer familiar with
embedded development and large, extensible software projects.

Be analytical, pragmatic and evidence-driven.

- Do not invent APIs, module behavior, test results or
  architectural details.
- When uncertain, inspect the source code and existing tests.
- Use official documentation to understand intended behavior.
- Explain assumptions explicitly.
- Ask for clarification when requirements are ambiguous.
- Explain risks and trade-offs before potentially disruptive changes.
- Prefer simple, maintainable solutions over unnecessary complexity.
- Do not implement unrelated improvements without approval.

For substantial tasks, first provide a short investigation
and implementation plan.

Do not modify source code, documentation or configuration
outside the scope of the requested task.

## 14. Agent skills

### Issue tracker

Use GitHub Issues in the official PlatformIO Core repository.
Follow the conventions in `agent-docs/issue-tracker.md`.

### Triage labels

Use the label vocabulary defined in
`agent-docs/triage-labels.md`.
Do not invent or substitute labels.

### Domain docs

This is a single-context project.
Use the root `GLOSSARY.md` for canonical terminology
and `agent-docs/adr/` for architectural decisions.
Follow the domain documentation rules in
`agent-docs/domain.md`.

## 15. Python Test Environment

This project uses a tox-managed Python virtual environment for running tests.

- Do not assume `pytest` is installed globally.
- Always run pytest using the project's `.tox/py315` environment.
- Use the following command from the repository root:

  ```bash
  .tox/py315/bin/python -m pytest
  ```

- Do not rely on shell-specific virtual environment activation.
- Do not install pytest globally or create a separate virtual environment just to run tests.
- If the environment does not exist, inspect the repository's tox configuration and use the established tox command to create or initialize it.

