# Security

Orbit 0.1.2 addresses the local privilege and Android event-injection findings
identified in the October 2026 review.

- Windows runs without administrator privileges and refuses an elevated launch.
  The installer removes the old `Orbit` elevated scheduled task and installs into
  Program Files. Normal startup uses the current user's Run registry value.
  Windows press-and-hold tracing is disabled until it can use a protected helper;
  rotation and single/double/triple presses continue to work.
- Windows launch targets are resolved as files, executables, or installed apps;
  unresolved names are never interpreted as shell commands.
- Android's exported launcher ignores test extras. The debug broadcast injector
  exists only in debug builds and requires the system DUMP permission.
- Android's externally invoked hold activity requires an unobscured confirmation
  on an unlocked device. Incoming events and pending actions are blocked while
  Orbit is off. Oversized rotation inputs are rejected.
- Desktop developer input requires a random session secret, enforces event bounds
  and a rate limit, and is excluded from production packages. Single-instance IPC
  is restricted to the current user.
- Desktop build inputs are pinned with hashes, Actions are pinned to commits,
  and the Gradle download is checked against its published SHA-256. Kotlin is
  upgraded to 2.4.21, which includes the KAPT cache-deserialization fix.
- Android release builds never fall back to a debug signing key. The publishing
  workflow requires private release credentials and verifies the APK signature.
  Only the release publishing job receives repository write permission.

The fork's Android release application ID is `app.orbit.dial.chaudharysk`, allowing
installation alongside the original app. Its private signing key is held outside
Git and in encrypted repository Actions secrets. Keep a private backup of that
key; replacing it prevents future APKs from updating existing fork installations.

Windows installers remain unsigned and macOS builds remain ad-hoc signed unless
a distribution signing identity is provided. Fixing application security does not
provide a Microsoft/Apple publisher certificate or Apple notarization. Downloads
include SHA256SUMS.txt so files can be checked against the published release.

Automated checks cover Python behavior, rejected developer inputs, privilege
refusal, Android engine input validation and disabled-state behavior, native API
smoke tests, packaging, and both debug/release Android unit tests. Physical buds
and phones still need hardware acceptance testing.
