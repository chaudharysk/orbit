# 0.1.2 security update

- Windows runs without administrator privileges. The installer removes the old
  elevated startup task; sign-in startup now runs as the normal user.
- Windows press-and-hold tracing is disabled pending a protected helper. Rotation
  and single/double/triple press controls remain available.
- Android ignores external test extras, confirms hold requests on an unlocked
  device, and blocks dial actions while off.
- Developer input is authenticated and unavailable in packaged desktop builds.
- Build dependencies and Actions are pinned, Gradle downloads are verified, and
  Kotlin includes the build-cache security fix. Android APK signing is verified.
- This fork's Android build installs separately from upstream using application
  ID `app.orbit.dial.chaudharysk`.
- macOS now requires version 14 or newer for the pinned Qt release.

Windows/macOS builds do not have commercial publisher signing/notarization.
See SECURITY.md for the security changes and remaining platform limitations.

---

**Orbit 0.1.1**: fixes from the first wave of users. Thank you for the reports!

**Fixed**
- **Wheel never opened on some phones** (#1): presses that the phone delivers as play / next / previous commands (seen on Android 16, Nothing phones) are now picked up, and Android's volume readings in a different scale no longer turn one click into three.
- **Couldn't find Orbit on Windows** (#2): starting Orbit again now opens its Settings, the first launch says where it lives, clicking the tray icon opens Settings, and the tray icon is a bright ring that's visible on dark and light taskbars.

**New**
- **On / off switch everywhere.** Off = the buds work normally (press plays / pauses, the dial changes volume). Windows / Mac: tray menu → Orbit on. Android: the app's switch, Turn off on the notification, or the Orbit Quick Settings tile.
- **Teleprompter tool (Android, off by default):** turn to move the script, press to play / pause, for apps like NEEWER Teleprompter. Switch it on in the app's Wheel items. While it's active, no pop-ups cover the script.
- **Simpler Android home:** the on/off switch, setup that tucks away into "All set" once done, then your wheel and gestures. Help → "Wheel won't open?" shows when presses reach Orbit and how to set the dial in Nothing X; "Report a problem" copies the log.
- **Smaller, lower pop-up** on Android when you use a tool, so it covers less of the screen.
- The tray menu shows whether the buds are connected.

**Important:** Orbit needs the dial set to *single press = Play/Pause, double = Next track, triple = Previous track, hold = Voice assistant* in the Nothing X app.

**Downloads** (Assets below): Windows `Orbit-Windows-Setup.exe` · macOS `Orbit-macOS.zip` · Android `Orbit-Android.apk`.
