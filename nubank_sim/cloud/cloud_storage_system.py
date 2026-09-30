from abc import ABC, abstractmethod


class CloudStorageSystem(ABC):
    """
    `CloudStorageSystem` interface.

    All sizes and capacities are non-negative integers. `timestamp` is a
    strictly increasing integer (milliseconds); every call receives a
    `timestamp` greater than any previous call.
    """

    # -------------------- Level 1 --------------------
    @abstractmethod
    def add_file(self, timestamp: int, name: str, size: int) -> bool:
        """
        Create a new file called `name` with the given `size` in the
        ownerless (global) namespace.
        Return True if created, or False if a file with `name` already
        exists.
        """
        return False

    @abstractmethod
    def get_file_size(self, timestamp: int, name: str) -> int | None:
        """
        Return the current size of `name`, or None if it doesn't exist.
        """
        return None

    @abstractmethod
    def delete_file(self, timestamp: int, name: str) -> int | None:
        """
        Delete `name` and return the size it had, or None if it doesn't
        exist.
        """
        return None

    # -------------------- Level 2 --------------------
    @abstractmethod
    def get_n_largest(self, timestamp: int, prefix: str, n: int) -> list[str]:
        """
        Return the identifiers of the `n` largest files (by size) whose name
        starts with `prefix`, sorted in descending order of size. Ties are
        broken alphabetically by name in ascending order.

        Each entry is formatted as `"<name>(<size>)"`.
        If fewer than `n` files match, return all of them.

        This must consider every file currently in the system, regardless
        of whether it was created via `add_file` or `add_file_by`.
        """
        return []

    # -------------------- Level 3 --------------------
    @abstractmethod
    def add_user(self, timestamp: int, user_id: str, capacity: int) -> bool:
        """
        Create a new user with the given total storage `capacity`.
        Return True if created, or False if `user_id` already exists.
        """
        return False

    @abstractmethod
    def add_file_by(self, timestamp: int, user_id: str, name: str, size: int) -> int | None:
        """
        Add a file called `name` owned by `user_id`. A file name only needs
        to be unique within that user's own namespace.
        Return the user's remaining capacity (`capacity - total used`) after
        adding the file, or None if: the user does not exist, the user
        already owns a file called `name`, or adding the file would exceed
        the user's capacity.
        """
        return None

    @abstractmethod
    def delete_file_by(self, timestamp: int, user_id: str, name: str) -> int | None:
        """
        Remove `user_id`'s file called `name`.
        Return the user's remaining capacity after the removal, or None if
        the user does not exist or does not own a file called `name`.
        """
        return None

    # -------------------- Level 4 --------------------
    @abstractmethod
    def merge_user(self, timestamp: int, user_id_1: str, user_id_2: str) -> bool:
        """
        Merge `user_id_2` into `user_id_1`: capacities are summed and all of
        `user_id_2`'s files become owned by `user_id_1`. If an incoming file
        name collides with one `user_id_1` already owns, the incoming file
        is renamed by appending " (merged)" (repeated if still colliding) to
        stay unique. After the merge, `user_id_2` no longer exists.
        Return True on success, or False if `user_id_1 == user_id_2` or
        either user does not exist.
        """
        return False

    @abstractmethod
    def backup_user(self, timestamp: int, user_id: str) -> int | None:
        """
        Save a snapshot of `user_id`'s current capacity and full set of
        owned files. A later call to `backup_user` for the same user
        overwrites the previous snapshot.
        Return the number of files captured in the snapshot, or None if the
        user does not exist.
        """
        return None

    @abstractmethod
    def restore_user(self, timestamp: int, user_id: str) -> int | None:
        """
        Restore `user_id`'s capacity and files to the most recent snapshot
        taken by `backup_user`, discarding any changes made since (including
        files or capacity gained through a later `merge_user`).
        Return the number of files restored, or None if the user does not
        exist or has no snapshot.
        """
        return None
