# RetroAchievements 16546 on Saturn

Checked on November 18, 2026. The [official Sakura Taisen entry](https://retroachievements.org/game/16546) shows 68 base achievements, 499 points, and six leaderboards. This research verifies disc identification and the integration contract. The authenticated download of the condition catalog, testing its triggers, and integration with an account remain pending.

## Disc identification

rcheevos' Saturn reader opens track 1 and reads the first 512 bytes of data from the initial sector, which carries the Saturn signature. The hash identifies the header and only covers those 512 bytes. [Identification method](https://docs.retroachievements.org/developer-docs/game-identification.html#sega) · [rcheevos v12.5.0 code](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rhash/hash_disc.c#L1191-L1218).

A private program was compiled with the official rcheevos v12.5.0 and `rc_hash_generate` was called with `RC_CONSOLE_SATURN` (39) against the prepared CUE files. The results also matched the MD5 of the first 512 bytes of the MODE1/2048 ISO track. Both rows correspond to the published hashes for game 16546. [Official hashes](https://retroachievements.org/game/16546/hashes).

| Local entry | Hash computed by rcheevos | Official label |
| --- | --- | --- |
| Disc 1, English v2.1 | `c4db9d08d56d1fbf78322852775d4818` | Japan · Disc 1 (6M) |
| Disc 2, English v2.1 | `c306c094d0177459b31f411cd4cd44a9` | Japan · Disc 2 (6M) |
| Disc 1, local Spanish build | `c4db9d08d56d1fbf78322852775d4818` | Japan · Disc 1 (6M) |

The hash alone does not allow distinguishing these translations from the table's Japanese editions. Enabling future evaluation and submission requires identifying the full local media and validating reads and conditions per variant. The disc 2 test computes its identity. Changing disc naturally requires testing session continuity and passing the incoming medium's hash through rcheevos' media-change API. [`rc_client` integration](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration) · [Translation compatibility testing](https://docs.retroachievements.org/guidelines/content/player-compatibility-testing.html).

## Memory map

rcheevos' map expresses ranges as RetroAchievements offsets and two 1 MiB regions. The local SDK exposes `satrecomp::Ram` with both banks and guest bytes in big-endian order. [Saturn map in rcheevos v12.5.0](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rcheevos/consoleinfo.c#L863-L869).

| RetroAchievements range | Saturn bank | Initial SH-2 address |
| --- | --- | --- |
| `0x000000–0x0FFFFF` | Work RAM Low | `0x00200000` |
| `0x100000–0x1FFFFF` | Work RAM High | `0x06000000` |

The proposed adapter would read bytes directly and clamp each span to the end of its bank before continuing into the next. Addresses from `0x200000` fall outside the map. rcheevos interprets the byte order requested by the condition. The check must cover boundary reads, multi-byte reads, byte order, resets, disc change, and loaded states. Evaluate once per confirmed frame and skip run-ahead iterations, rendering, and diagnostic replays. Use reads on the thread that owns the machine and flush network events on that same thread. Coordinate resetting or restoring condition state when loading states, with serialization bounded through the client API. [Memory callback and execution API](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/include/rc_client.h).

## Catalog, badges, and connection

| Block | Documented flow |
| --- | --- |
| 1:1 catalog | Use the set approved by the service and its IDs, text, points, and conditions. `rc_client_create_achievement_list` represents the loaded set. The Game Extended web API delivers metadata with a web API key and serves a different purpose. The public HTML provides an inventory reference. |
| Badges | Use the URL returned by `rc_client_achievement_get_image_url` for the locked or unlocked state. Cache by ID and state in the profile, with cache limits and a visual fallback if the image is missing. |
| Login | Ask for a password only when logging in, then keep the token per account if the user enables Remember. Use `rc_client_begin_login_with_password` or `rc_client_begin_login_with_token`. The host supplies asynchronous HTTPS transport, limits, and UI. |
| Casual mode and disconnection | Initialize with Hardcore disabled. The client retries transient award failures within the active session and publishes disconnect/reconnect events. The host keeps servicing `rc_client_idle` while the game is paused. |
| Offline startup and persistence | Keep separately a verified local copy of the set, the offline history, and the queue for an authenticated account. Initializing a new session without internet requires resolving the origin and cache rules for conditions. rcheevos' in-memory queue alone is lost on exit. |

[`rc_client` API](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration) · [Client retries](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rc_client.c#L4615-L4705) · [Game Extended](https://api-docs.retroachievements.org/v1/get-game-extended.html) · [Badge guide](https://docs.retroachievements.org/guidelines/content/badge-and-icon-guidelines.html).

The ReKHCoM pattern separates local achievements without an account, Casual online session, and retries after losing network. Its source keeps a dated per-user queue and validates an enabled subset of conditions for compatible media. Its validation document deliberately separates RAM mapping, local testing, and official enablement. Saturn must validate its own map and its own conditions. [ReKHCoM client](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/achievements/ra_client.c) · [Offline persistence](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/achievements/offline_achievements.c) · [ReKHCoM validation](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/progress/RETROACHIEVEMENTS_71_VALIDACION.md).

## Checkable pending items

- Review the integration path and per-medium compatibility before syncing with an account. The Standalone guide excludes unofficial ports from that category's sets. Here the existing Saturn set is studied via its canonical memory map. The `rc_client` guide mentions client identification with a User-Agent for Hardcore. Local development and Casual-mode testing with simulated transport can advance in parallel with this review. Official compatibility and account sync remain unverified. [Standalone Support](https://docs.retroachievements.org/general/standalone-support.html) · [`rc_client` integration](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration).
- Obtain the catalog through a supported channel, log the revision and distinct IDs, and check their parity. Keep responses, badges, and progress in local cache. Before considering a from-scratch, no-network startup with 68 conditions, confirm the set's distribution or installation path.
- Test reads and triggers first with disconnected transport and memory captured along natural paths against a Saturn reference. Include false positives on saves, reset, disc transition, and state loading. Test login, expiration, retries, per-account storage, and reopening the queue against a simulated server before an authorized sync test.
- Keep unlocks obtained without an account as local progress. Retries from an authorized session must keep the user, game, hash, ID, and origin date, and should only be removed after service confirmation. Paths that grant or sync achievements require client and session validation.

This research did not log in, did not submit unlocks, and did not update the service. The sources, the probing executable, its hash log, and the reference reads are kept in the private research folder.
