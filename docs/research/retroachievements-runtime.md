# RetroAchievements runtime

Patch 0106 integrates rcheevos 12.5.0 for Sakura Taisen game 16546. The launcher accepts a RetroAchievements username and session token. It validates the token over HTTPS before saving it with Windows DPAPI in the current profile. The launcher shows the last session state, locked and unlocked entries, points, cached badges, and local synchronization history.

The Saturn adapter checks the first-track system area against the two known rcheevos identifiers. It reads work RAM Low and High in guest byte order and advances the client once after each confirmed frame. While the game is paused the host handles network callbacks without evaluating another frame. State and movie diagnostics skip online evaluation. The existing release marker keeps development states out of packages. State and reset-point actions are also disabled during an achievements session.

The popup draws in a margin outside the native, dialogue, and choice viewports. It waits for space to appear when the window has no suitable margin. The badge comes from the allowlisted HTTPS CDN and is cached in the profile. The popup can show the title and points while the image is unavailable.

On a verified online start, the profile caches the set and the session's unlock information. A later connection failure can use this cache for the same account and disc. Offline unlocks persist before network delivery and are retried on the next verified online start. Records keep the original game, disc, ID and timestamp. The queue removes a record after a matching acknowledgement or when authenticated progress confirms the award. An offline first launch requires a previously cached set to evaluate official conditions.

## Verification

Run the Windows fixture suite with python tests/ra/run.py --rcheevos <local-rcheevos-12.5.0-source> after applying the SDK patches.

- Offline executable tests in `tests/ra` use actual rcheevos with an in-process service and synthetic conditions. They check RAM bank boundaries, header hashing, token login, disc media changes, queue isolation, cold offline startup, restart retry, acknowledgement, encrypted credential round trips, badge delivery and connection status.
- An isolated runtime with a synthetic condition triggered from a natural Saturn Work RAM transition at guest frame 167. In Original and Enhanced at 1280 × 720, each on/off pair matched all 230 guest hashes with zero interpreted blocks. The enabled window changed only within (6, 6)–(154, 64), the badge popup. The mock confirmed the same award and the local activity log recorded it. The launcher was built separately and displayed the synthetic badge, 1 of 1 achievements, and 5 points.
- Private replay scripts, captures and receipts are in `local/work/codex-tra`. The simulated service had no network transport or real account credentials.

The official conditions and translated media need validation against the Saturn reference. The test verified disc 2 through the rcheevos media API fixture. A live optical-disc transition in the game is still open. A real account login and synchronized unlock require coordinated authorization and a naturally earned achievement. Casual is the service mode until the project and media are eligible for Hardcore. No release package was produced.
