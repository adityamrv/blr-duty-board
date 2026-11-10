#!/usr/bin/env bash
# Builds the Duty Board Android app (duty-board.apk). Run by .github/workflows/android-app.yml.
# The app is a thin shell: it opens the live web app and adds the phone's alarm system for alerts.
set -euo pipefail
cd "$(dirname "$0")"

npm ci
rm -rf android
npx cap add android

APP=android/app
# 1. Exact alarms without a settings prompt (Android 13+). The notification plugin already declares the rest.
python3 - "$APP/src/main/AndroidManifest.xml" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
perm = '    <uses-permission android:name="android.permission.USE_EXACT_ALARM" />\n'
assert "<application" in s
if "USE_EXACT_ALARM" not in s:
    i = s.index("<application"); i = s.rfind("\n", 0, i) + 1
    s = s[:i] + perm + s[i:]
open(p, "w").write(s)
PY
# 2. App icon: plain PNGs made from icons/icon-512.png
rm -rf "$APP/src/main/res/mipmap-anydpi-v26"
cp -r res/. "$APP/src/main/res/"
# 3. Fixed signing key (so a new build installs over the old one and keeps the phone's data),
#    version number from the build run, and no lint stop on release builds.
cat >> "$APP/build.gradle" <<GRADLE

android {
    defaultConfig {
        versionCode ${GITHUB_RUN_NUMBER:-1}
        versionName "1.${GITHUB_RUN_NUMBER:-0}"
    }
    signingConfigs {
        fixed {
            storeFile file("../../dutyboard.keystore")
            storePassword "dutyboard"
            keyAlias "dutyboard"
            keyPassword "dutyboard"
        }
    }
    buildTypes {
        release { signingConfig signingConfigs.fixed }
    }
    lint {
        checkReleaseBuilds false
        abortOnError false
    }
}
GRADLE

npx cap sync android
(cd android && chmod +x gradlew && ./gradlew --no-daemon assembleRelease)
cp "$APP/build/outputs/apk/release/app-release.apk" duty-board.apk
ls -l duty-board.apk
