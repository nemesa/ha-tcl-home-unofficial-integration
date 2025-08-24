# TCL Home – Comprehensive Research (Curated, Full Detail)

## Research notes contain:
- APK reverse engineering
- React Native panel delivery 
- network captures (including CA install on emulator)
- evidence for portable AC fan speeds
- and practical repro steps
- Implementation specifics are intentionally out of scope, but integration ideas are outlined.


## Context
- Repository: Home Assistant custom component `tcl_home_unofficial`.
- Goal: Understand how the official TCL app communicates with AWS IoT and how model UI/config determines portable AC fan‑speed semantics (especially Medium), then translate that knowledge into robust integration behavior.

Terms (quick glossary)
- Panel: React Native UI package (bundle + assets) that renders a device’s control screen for a product family.
- productKey: Identifier for a product/model family; used to pick which panel to download.
- rnVersion: Version of the React Native panel for a given productKey.
- Thing Shadow: AWS IoT device state document; read via GET shadow and written via shadow/update.
- IoT Data REST vs WSS: Shadow over HTTPS (REST) and MQTT over WebSocket; both can appear in captures.

## Folder Map (Local Research - files are not included)
- APK decompiled: `research/APK Decomplied/`
- React Native bundle (extracted): `research/RN-Bundle-Decompressed/com.tcl.panel_ac_overseas_nv3.0.6/`
- MITM captures: `research/MITM TCL App Decryption/Captures/`

## Part 1 — APK App Decompilation

What we examined
- APK version: `com.tcl.tclhome_4.9.6-1165_minAPI23` (decompiled under APK Decomplied/).
- Evidence that React Native UI is delivered at runtime; Matter ↔ TSL mapping; AWS IoT usage.

Key classes and assets (decompiled paths)
- Matter mapping and delegates:
  - `research/APK Decomplied/com.tcl.tclhome_4.9.6-1165_minAPI23/sources/com/tcl/tclhome/matter/util/ACMatterTSL.java`
  - `.../sources/com/tcl/tclhome/matter/delegate/ACMatterDelegate.java`
- AWS IoT / shadow managers:
  - `.../sources/com/tcl/bmmqtt/manager/IotMqttManager.java`
- React Native bootstrap and registrars (obfuscated packages containing React Native bridge/types):
  - `.../sources/i/w/d0/c/a.java` (RnPackageManager)
  - `.../sources/i/w/d0/b/a.java`, `.../sources/i/w/d1/b/b.java`, `.../sources/i/a/a/a/a/b.java`, `.../sources/i/w/d1/e/a.java`
- Assets implying runtime React Native delivery:
  - `research/APK Decomplied/com.tcl.tclhome_4.9.6-1165_minAPI23/resources/assets/host.json`
  - `research/APK Decomplied/.../assets/host_odm.json`
  - `research/APK Decomplied/.../assets/iot_download_rn.json`

What we learned from APK
- The app uses AWS IoT SDK (REST + WSS MQTT) to read/write the Thing Shadow.
- Matter ↔ TSL code paths imply canonical Auto/Low/Med/High mapping for supported ACs.
- Portable capabilities are not clearly exposed as a simple “3 speeds” bit in Java; React Native layer and model templates drive UI.

## Part 2 — Installed App Data (Emulator Artifacts)

Observed on a rooted Android emulator during app usage
- React Native panel cache (internal): `/data/data/com.tcl.tclhome/files/tSmart_RN/com.tcl.panel_ac_overseas_nv3.0.6/`
  - Contains `main.jsbundle` (~2.9 MB, plain JS for this panel) and `manifest.json` (`productKey`, `packageName`, `rnVersion`).
- SharedPrefs: `com.amazonaws.android.auth.xml` present (encrypted), confirming Cognito region (e.g., `eu-central-1`).
- MMKV stores: `files/mmkv/{unprotected,protected}` (binary, likely feature flags/caches).
- External cache: `/sdcard/Android/data/com.tcl.tclhome/cache/download_cache/` contains React Native panel zips and small config JSON files.

Offline behavior expectation
- Fresh install + offline before first open: AC panel likely fails to render (bundle not cached yet).
- After first online open: panel should render offline until cache invalidation or version bump.

## Part 3 — React Native Panel ZIP (How To Get It, What It Contains)

How the app gets the React Native panel
- ProductKey‑scoped, versioned by `rnVersion`. Hosts include `eu-h5-prod.aws.tcljd.com` (and `us-`, `in-`, `br-`).
- Example URL: `https://eu-h5-prod.aws.tcljd.com/<productKey>/android/<rnVersion>/release_android.zip`.
- App learns `rnVersion` and `packageName` from TCL config endpoints observed in captures:
  - `GET /v3/config/uxp/get?countryCode=<abbr>`
  - `POST /v3/config/get` (payload includes `productKey`) — responses list React Native module info.

How you can fetch and inspect
- From device external cache (after opening panel once):
  - `adb shell ls -lR /sdcard/Android/data/com.tcl.tclhome/cache/download_cache/`
  - `adb pull /sdcard/Android/data/com.tcl.tclhome/cache/download_cache/<zip>.1 ./research/RN-Bundle-Decompressed/`
  - `unzip -o <zip>.1 -d ./research/RN-Bundle-Decompressed/`
- From internal cache (if accessible):
  - `adb pull /data/data/com.tcl.tclhome/files/tSmart_RN/com.tcl.panel_ac_overseas_nv3.0.6 ./research/RN-Bundle-Decompressed/`

What the panel contains (portable AC panel)
- `main.jsbundle` (plain JS, minified).
- `manifest.json` — includes `productKey`, `packageName` (e.g., `com.tcl.panel_ac_overseas_nv`), `rnVersion`.
- Images/drawables including speed icons for Auto/Low/Mid/High.

Local reference
- Extracted bundle: `research/RN-Bundle-Decompressed/com.tcl.panel_ac_overseas_nv3.0.6/`

## Part 4 — TLS Decryption & Network Capture (Emulator + PCAPdroid)

Purpose
- Decrypt all TCL app traffic on an Android 12 AVD, capture it with PCAPdroid, and analyze with Wireshark/TShark.

Prereqs
- Android 12 AVD (AOSP image) available.

One-time setup: install PCAPdroid + system CA
1) Start emulator with writable system:
   - `~/Android/Sdk/emulator/emulator -avd Medium_Phone -writable-system -no-snapshot`
2) Enable root and remount system:
   - `adb root && adb remount`
3) Install PCAPdroid on the emulator (AOSP has no Play Store):
   - Download the PCAPdroid APK to your host (e.g., from F-Droid).
   - `adb install ~/Downloads/PCAPdroid.apk`
4) Export PCAPdroid CA on the emulator:
   - PCAPdroid → Settings → TLS decryption → Export CA (saves to `/sdcard/Download/pcapdroid_ca.pem`).
5) Convert CA to legacy subject-hash filename and push to system store:
   - Convert to DER: `openssl x509 -in pcapdroid_ca.pem -outform DER -out 81c450f1.0`
   - Or compute hash: `openssl x509 -inform PEM -in pcapdroid_ca.pem -subject_hash_old -noout` → e.g., `81c450f1`; save as `81c450f1.0`
   - `adb push 81c450f1.0 /system/etc/security/cacerts/`
   - `adb shell chmod 644 /system/etc/security/cacerts/81c450f1.0`
   - `adb shell chown root:root /system/etc/security/cacerts/81c450f1.0`
6) Reboot emulator and verify app-wide TLS decryption in PCAPdroid.

Tools and artifacts
- Capture: PCAPdroid (VPN-based sniffer with TLS MITM when CA is trusted system-wide).
- Analysis: Wireshark/TShark using TLS key log file for decryption.
- Example outputs (already pulled into repo):
  - PCAP: `research/MITM TCL App Decryption/Captures/PCAPdroid_20_Aug_13_45_17.pcap`
  - Keylog: `research/MITM TCL App Decryption/Captures/sslkeylogfile.txt`

Capture workflow (each session)
1) Open PCAPdroid on the emulator.
2) In PCAPdroid Settings → TLS decryption:
   - Enable “TLS decryption”.
   - Ensure the PCAPdroid CA is installed as a system CA (one-time setup above).
   - Enable “Export SSL key log file” (or equivalent option).
   - Add the TCL app to Encryption rules so traffic is decrypted:
     - Settings → TLS decryption → Encryption rules → + → App → select `com.tcl.tclhome` → Action: Decrypt.
3) Start capture in PCAPdroid and accept the VPN prompt.
4) In the TCL app, perform the actions you want to capture (login, open AC panel, change fan speeds, etc.).
5) Stop capture in PCAPdroid.
6) Export files from PCAPdroid to device storage (Downloads):
   - Export PCAP: e.g., `/sdcard/Download/PCAPdroid_YY_MMM_DD_HH_MM_SS.pcap`
   - Export TLS key log: e.g., `/sdcard/Download/sslkeylogfile.txt`

Pull captures to host
- `adb shell ls -l /sdcard/Download | sed -n '1,200p'`
- `adb pull /sdcard/Download/PCAPdroid_*.pcap "research/MITM TCL App Decryption/Captures/"`
- `adb pull /sdcard/Download/sslkeylogfile.txt "research/MITM TCL App Decryption/Captures/"`

Decrypt and inspect with Wireshark (GUI)
- Open the PCAP in Wireshark.
- Preferences → Protocols → TLS → (Pre)-Master-Secret log filename → select `sslkeylogfile.txt`.
- Apply display filters, e.g. `http` or `http.host contains data.iot`.

Decrypt and inspect with TShark (CLI)
- List IoT Data REST requests:
  - `tshark -r "research/MITM TCL App Decryption/Captures/PCAPdroid_20_Aug_13_45_17.pcap" -o tls.keylog_file:"research/MITM TCL App Decryption/Captures/sslkeylogfile.txt" -Y "http.request and http.host contains data.iot" -T fields -e frame.number -e http.request.method -e http.request.uri`
- Print HTTP bodies (may include JSON shadow updates):
  - `tshark -r "research/MITM TCL App Decryption/Captures/PCAPdroid_20_Aug_13_45_17.pcap" -o tls.keylog_file:"research/MITM TCL App Decryption/Captures/sslkeylogfile.txt" -Y "http.file_data and http.host contains data.iot" -T fields -e http.file_data`

HTTP/2 note
- IoT Data REST often uses HTTP/2. If bodies seem missing under basic `http` filters, try Wireshark’s “Follow HTTP/2 stream”, or TShark with `-Y http2` to confirm streams, then apply `http.file_data`.

Endpoints observed (SNI/hosts)
- TCL cloud REST/config: `us.account.tcl.com`, `pa.account.tcl.com`, `prod-eu.aws.tcljd.com`, `eu-default-prod.aws.tcljd.com`, `eu-h5-prod.aws.tcljd.com`, `prod-center.aws.tcljd.com`, `prod-cms-resource.aws.tcljd.com`, `tracking-*.*.tcljd.com`, `discovery.bd.tcljd.com`.
- AWS identity + IoT: `cognito-identity.<region>.amazonaws.com`, `iot.<region>.amazonaws.com`, `data.iot.<region>.amazonaws.com`, AWS IoT WSS endpoint `*.iot.<region>.amazonaws.com:443`.

Notes
- Without a keylog/CA, TLS traffic remains encrypted (expected). With a system CA and writable-system emulator, app-wide TLS decryption works for this setup.

## Part 5 — IoT Payload Observations (Ground Truth)

Observed IoT Data REST interactions (from decrypted capture)
- Shadow GET (authoritative state):
  - `GET /things/<deviceId>/shadow` → fields in `state.{desired,reported}` such as `powerSwitch`, `windSpeed`, `swingWind`, `workMode`, `target*`, `currentTemperature`, `temperatureType`, `sleep`, `errorCode`; often no `capabilities` on portables.
  - Example (redacted):
    {
      "state": {
        "desired": {"powerSwitch":1, "workMode":1, "windSpeed":2},
        "reported": {"powerSwitch":1, "workMode":1, "windSpeed":2}
      },
      "metadata": {"desired": {...}, "reported": {...}},
      "version": 1234,
      "timestamp": 1724150000
    }
- Shadow UPDATE:
  - `POST /topics/%24aws/things/<deviceId>/shadow/update?qos=1` with bodies like:
    - `{ "state": { "desired": { "windSpeed": 2 } } }` (Medium)
    - Also observed 0 (Auto), 1 (Low), 3 (High), with concurrent mode/temp updates.

Product identity vs device identity
- `productKey` identifies the model family and selects the React Native panel.
- `deviceId`/`thingName` is unique per device and is used in shadow topics.

## Part 6 — Evidence From React Native Panel (Portable AC)

Panel artifacts show support for Medium
- Assets/strings include: auto/low/mid/high status and icons.
- Ordered mapping found in code:
  - `new Map([['FAN_SPEED_AUTO',0],['FAN_SPEED_LOW',1],['FAN_SPEED_MED',2],['FAN_SPEED_HIGH',3]])`
- Confirms panel can render Medium and maps it to `2` when applicable.

## Part 7 — Integration Behavior Snapshot (Current)

Integration code context
- Device listing via TCL REST (signed headers with SAAS token) — not from IoT.
- Live operational state and control via AWS IoT Device Shadow.
- Feature detection for portables currently uses presence of fields (e.g., `windSpeed`, `swingWind`). No explicit “three speeds” flag.
- For some portable devices, selects expose only Low/High (+Auto in some modes), omitting Medium.

Evidence from repo diagnostics
- A real device diagnostic shows `"windSpeed": 3` in desired/reported while in Cool mode, implying a 0..3 model.

## Part 8 — Working Deductions

Portable windSpeed families
- Two‑step models: Auto + Low/High with constrained values.
- Three‑step models: Auto + Low/Med/High with values 0..3.

React Native UI decision making
- Likely driven by product schema and React Native panel code/templates rather than a portable capability bit in Java.

## Part 9 — React Native Bundle Capture Checklist (Static Analysis)

Prereqs
- Android device/emulator with USB debugging; `adb`; local disk space.

Steps
- Optional reset: `adb shell pm clear com.tcl.tclhome`.
- Trigger React Native panel download: open AC control screen in app.
- Inspect internal cache (may require root): `adb shell run-as com.tcl.tclhome ls -R files cache`.
- Inspect external cache: `adb shell ls -R /sdcard/Android/data/com.tcl.tclhome/` for `*.bundle` or versioned ZIPs.
- Pull bundle: `adb pull /data/data/com.tcl.tclhome/files/tSmart_RN/com.tcl.panel_ac_overseas_nv3.0.6 ./research/RN-Bundle-Decompressed/`
- Grep interesting strings in bundle/dump: `windSpeed`, `FanMode`, `AUTO|LOW|MED|HIGH`.
- Archive artifacts: raw bundles, dumps, referenced source maps, and `manifest.json`.

## Part 10 — IoT Payload Interception Checklist (Dynamic)

Prereqs
PCAPdroid; a device‑trusted CA (system store recommended on Android ≥7).

Approach
- Configure proxy and install system CA; enable app-wide TLS decryption in PCAPdroid (or your proxy tool).
- Focus on:
  - TCL REST for session/config: `/v3/user/get_things`, `/v3/auth/refresh_tokens`, `/v3/config/uxp/get`, `/v3/config/get`.
  - AWS IoT Device Shadow REST: `GET /things/<deviceId>/shadow`, `POST /topics/%24aws/things/<deviceId>/shadow/update?qos=1`.

TShark examples
- List IoT Data REST requests:
  - `tshark -r "research/MITM TCL App Decryption/Captures/PCAPdroid_20_Aug_13_45_17.pcap" -o tls.keylog_file:"research/MITM TCL App Decryption/Captures/sslkeylogfile.txt" -Y "http.request and http.host contains data.iot" -T fields -e frame.number -e http.request.method -e http.request.uri`

## Part 12 — Confirmed Findings (Example ProductKey)

Portable AC example (productKey `(redacted)`)
- React Native bundle shows Auto/Low/Med/High assets and mapping.
- IoT Data REST updates observed:
  - `{ "state": { "desired": { "windSpeed": 2 } } }` (Medium)
  - `{ "state": { "desired": { "windSpeed": 1 } } }` (Low)
  - `{ "state": { "desired": { "windSpeed": 3 } } }` (High)
  - `{ "state": { "desired": { "windSpeed": 0 } } }` (Auto)
- Shadow GET responses contain only desired/reported state; no `capabilities` array for this device.

## Quick Reference
- React Native panel cache on device: `/data/data/com.tcl.tclhome/files/tSmart_RN/`
- External cache: `/sdcard/Android/data/com.tcl.tclhome/cache/download_cache/`
- TShark decrypt with keylog: see Part 10.
- CA install on AVD: see Part 4 (legacy subject hash, push to `/system/etc/security/cacerts/`).
