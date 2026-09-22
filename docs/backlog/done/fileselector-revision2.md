---
type: task
updated: 2026-09-21
---

# File-selector crash and revision 2 package

Status: done locally; publication is separate.

Investigation of the reported `Scroll_fileselector -> strdup
-> strlen` crash, and a corrected package. Existing patch 0008 stopped the
crash but failed parent navigation on ABIv11; patch 0009 completes that fix.

Acceptance: reproduce the old crash, verify the packaged binary on AROS One,
check root/child navigation and filename editing, reconstruct the patch
series, and extract/check the LHA. These checks passed within the scope of
[the report](../../attachments/2026-09-21-fileselector/REPORT.md).
No image save/load roundtrip or guest LHA extraction was repeated.

Current behavior is consolidated in
[the current-state reference](../../current-state/overview.md#revision-2-file-selector-fix-2026-09-21).
