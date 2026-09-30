# Design a Cloud Storage System

You will implement an in-memory cloud storage system that grows in capability
across four levels. Each level builds directly on the previous one — do not
break earlier behavior when implementing later levels.

**General rules (apply to every level):**
- All sizes and capacities are non-negative integers.
- `timestamp` is a strictly increasing integer (milliseconds); every call
  receives a `timestamp` greater than any previous call.
- Methods return `None` (or `False`/`[]` where noted) to signal invalid
  operations rather than raising exceptions.

---

## Level 1 — Basic file operations

Implement a flat, ownerless file table.

- `add_file(timestamp, name, size) -> bool`
  Create a new file called `name` with the given `size`. Return `True` if
  created, or `False` if a file with that `name` already exists.

- `get_file_size(timestamp, name) -> int | None`
  Return the current size of `name`, or `None` if it doesn't exist.

- `delete_file(timestamp, name) -> int | None`
  Delete `name` and return the size it had, or `None` if it doesn't exist.

---

## Level 2 — Ranking by prefix

- `get_n_largest(timestamp, prefix, n) -> list[str]`
  Return the identifiers of the `n` largest files (by size, descending)
  whose name starts with `prefix`. Ties are broken alphabetically by name in
  ascending order. Each entry is formatted as `"<name>(<size>)"`. If fewer
  than `n` files match, return all of them. This must include files added
  through *any* mechanism introduced in later levels, not just `add_file`.

---

## Level 3 — Multi-user accounts with storage quotas

Users now own files. A file name only needs to be unique **within a single
user's namespace** — two different users may each have a file called
`"notes.txt"`. Files created via Level 1's `add_file` remain in a separate,
ownerless namespace.

- `add_user(timestamp, user_id, capacity) -> bool`
  Create a user with a total storage `capacity`. Return `False` if the user
  already exists.

- `add_file_by(timestamp, user_id, name, size) -> int | None`
  Add a file owned by `user_id`. Return the user's *remaining* capacity
  (`capacity - total used`) after adding, or `None` if: the user doesn't
  exist, the user already has a file called `name`, or adding the file
  would exceed the user's capacity.

- `delete_file_by(timestamp, user_id, name) -> int | None`
  Remove `user_id`'s file called `name` and return the user's remaining
  capacity afterward, or `None` if the user or file doesn't exist.

---

## Level 4 — Merging users and backup/restore

- `merge_user(timestamp, user_id_1, user_id_2) -> bool`
  Merge `user_id_2` into `user_id_1`: capacities are summed, and all of
  `user_id_2`'s files become owned by `user_id_1`. If a file name collides
  with one `user_id_1` already owns, the incoming file is renamed by
  appending `" (merged)"` (repeated if still colliding) to stay unique.
  After the merge, `user_id_2` no longer exists. Return `True` on success,
  or `False` if `user_id_1 == user_id_2` or either user doesn't exist.

- `backup_user(timestamp, user_id) -> int | None`
  Save a snapshot of `user_id`'s current capacity and full set of files.
  Calling this again overwrites the previous snapshot. Return the number of
  files captured, or `None` if the user doesn't exist.

- `restore_user(timestamp, user_id) -> int | None`
  Restore `user_id`'s capacity and files to the most recent snapshot taken
  by `backup_user`, discarding anything changed since (including files
  gained through a later `merge_user`). Return the number of files
  restored, or `None` if the user doesn't exist or has no snapshot.

---

## Files in this problem set

- `cloud_storage_system.py` — abstract interface (implement against this)
- `cloud_storage_system_impl.py` — reference solution
- `level_1_tests.py` … `level_4_tests.py` — 10 unit tests per level
