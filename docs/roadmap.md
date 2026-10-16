# Roadmap and feasibility gates

No calendar commitment is made before the hardware experiments. Each gate needs
recorded settings, evidence, limitations, and a decision to proceed or revise.

## Phase 1: Architecture and infrastructure

Accepted: Python/PySide6, explicit Equalizer APO integration, and matching at the
listening position. This milestone supplies architecture, contribution documents,
GitHub templates, repository CI, and development/release plans. It contains no
application implementation or runtime dependencies.

## Phase 2: Routing and measurement prototype

### Gate A: Windows route

Prove independent channel processing and bypass on the reference HDMI endpoint.
Verify fresh captures through the actual output path and test endpoint loss and
configuration restoration. If the APO cannot work reliably on this route, revisit
the backend decision before building the UI around it.

### Gate B: Measurement validity

Recover known synthetic filter responses and delays within documented tolerances.
Test clock mismatch and dropouts. Then demonstrate repeatable left/right captures
with the actual microphone chain and compare results with an independent tool.
Define numerical tolerances and quality thresholds before accepting results.

Identify the Audyssey model and PC input electrical compatibility first. Lack of
calibration must remain visible. Do not let an attractive plot substitute for
validated capture or synchronization.

## Phase 3: Speaker Matching MVP

### Gate C: Conservative matching

Show reduced reliable channel differences on fresh measurements, assess nearby
positions for regressions, and perform level-matched listening comparisons.
Reject unstable regions and accept that some sessions produce no useful correction.
Record limitations and test the complete filter/headroom behavior.

### Release scope

- Windows device selection and a minimal accessible measurement wizard.
- Repeated independent captures, quality checks, and response comparison.
- Conservative channel-specific parametric EQ and explicit headroom handling.
- Versioned local sessions and profile import/export.
- Equalizer APO setup guidance, activation, bypass, restoration, and verification.
- Honest limitations and a hardware compatibility matrix with tested versions.

## Phase 4: Cross-platform expansion

Implement and physically validate Linux/PipeWire routing as a first-class target.
Produce macOS builds only when an application exists; label them **Community
Testing Required** until actual testing supports a narrower compatibility claim.

## Phase 5: Advanced room correction

Consider multiple positions, target curves, wider correction bands, FIR filtering,
phase/time tools, and advanced controls after the matching workflow is useful.
Custom audio drivers, broad automatic installation, multichannel systems, and
automatic physical-defect diagnosis are outside the initial MVP.

## Public demonstration

Publish a real demonstration only after a usable prototype passes the gates.
Include original/verified measurements, hardware and routing details, processing
settings, and level-matched before/after audio with appropriate recording rights.
Do not imply universal performance from a single successful setup.
