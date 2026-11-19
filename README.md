# Fatawa Razviya — Jild 24 tashreeh v4 merge

Merge workspace: 17 leaf chunk files of the easy-Urdu tashreeh v4 for Fatawa Razviya Jild 24 (volume_id 39; 207 items, 640 pages) are merged into `jild-24.json` by GitHub Actions (`merge_jild24_v4.py`), then published as a v1.0 release asset.

Item order reproduces the v3 merged file exactly (first jild24-pesh-lafz, last jild24-masala-284). All 17 leaf chunks carry start_page == min(pages). No renames at merge — the tail id (jild24-risala-139) is absorbed by its cross-id join — and the merge joins 3 simple duplicate-id groups (masala-18 with sawal concat, masala-166, masala-250) plus the cross-id masala-84 (head + risala-139 tail), then stable-sorts by start_page, matching the v3 merged file. No page markers are present in the chunks.
