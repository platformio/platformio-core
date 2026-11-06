# PlatformIO Core — Domain Glossary

This document defines canonical terminology used throughout
PlatformIO Core development.

Use these definitions consistently in:
- Source code and comments.
- Issues and specifications.
- Tests and test names.
- Architecture discussions.
- Technical documentation.

Prefer established PlatformIO terminology over introducing
new synonyms.

When a concept is ambiguous or its definition changes,
clarify it before updating this glossary.

---

## Core Concepts

**PlatformIO Core**: The Python-based command-line core of the PlatformIO
ecosystem. It manages projects and packages, orchestrates builds, and integrates
with development platforms and tools.

**PlatformIO Project**: A project managed by PlatformIO Core, typically
containing a `platformio.ini` configuration file, source code, libraries, and
other project resources.

**Project Configuration**: The `platformio.ini` configuration and any included
extra configuration files that define project settings and environments.

**Project Environment**: A named `[env:<name>]` configuration processed for a
project; it can inherit common `[env]` settings.
_Avoid_: development environment, unqualified build environment.

**Build Configuration**: The `release`, `debug`, or `test` variant selected for
a project environment. It is distinct from the project environment and from a
debugging session.

## Embedded Development Concepts

**Development Platform**: PlatformIO's integration for a target architecture or
hardware family, including supported boards, frameworks, build scripts, and
tools.

**Platform Package**: An installable package of type `platform` that distributes
a development platform's definition and integration.

**Board**: A named configuration definition for supported hardware, supplying
presets such as build, upload, and debug settings.

**Target Device**: The physical hardware that receives firmware or whose program
execution is debugged.
_Avoid_: board definition.

**Framework**: A software framework selected for a project environment and
supported by its development platform; its implementation and build integration
may be supplied by packages.

**Toolchain**: The compiler, assembler, linker, and related tools used to
produce a program for a target architecture.

**Library**: Reusable software used by a project; it may be local,
framework-provided, or installed as a library package.
_Avoid_: package when referring to the software component rather than its
distribution.

## Package Management

**Package**: An installable item recognized by PlatformIO's package manager and
classified as a `library`, `platform`, or `tool`. Packages can come from sources
other than the Registry.

**Tool Package**: A package of type `tool` that can provide a toolchain or
auxiliary components such as a framework, SDK, uploader, or debugging server.

**Package Manager**: The infrastructure responsible for locating, installing,
updating, and managing PlatformIO packages.

**Package Registry**: A service where packages are published and discovered; it
is not the package manager or the only package source.

## Build and Execution

**Project Target**: An action processed by `pio run`, such as building,
uploading, cleaning, or monitoring. It is distinct from a target architecture or
device.

**Build**: Compilation and linking that produce program or firmware artifacts
for a project environment.

**Upload**: Transferring firmware to a target device, usually through an upload
tool and protocol; the `upload` target may trigger a build.

**Debugging**: Inspecting or controlling program execution on a target device; a
`debug` build configuration alone is not debugging.

---

## Terminology Rules

- Use `project environment` for `[env:<name>]`; use `build configuration` for `release`, `debug`, or `test`.
- Use `development platform` for the integration and `platform package` for its installable package.
- Distinguish a board definition from a target device, and a project target from target hardware.
- Use `framework` and `toolchain` for their roles, not as package-manager types.
- Use `package` for an installable item managed by PlatformIO; distinguish it from a library as source code and from the Registry as a package source.
- Do not introduce alternative names for established
  PlatformIO concepts without justification.

When adding or changing definitions, verify them against
the existing implementation and official documentation.
