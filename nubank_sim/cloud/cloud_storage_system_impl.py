from cloud.cloud_storage_system import CloudStorageSystem
from enum import Enum
from copy import deepcopy

class File:

    def __init__(self, timestamp, name, size) -> None:
        self.size = size
        self.name = name
        self.creation = timestamp

class Account:

    def __init__(self, name, capacity) -> None:
        self.name = name
        self.capacity = capacity
        self.used_capacity = 0
        self.files = {}
        self.snapshot: Account
        self.hasSnapshot = False

class CloudStorageSystemImpl(CloudStorageSystem):

    """
    `CloudStorageSystem` interface.

    All sizes and capacities are non-negative integers. `timestamp` is a
    strictly increasing integer (milliseconds); every call receives a
    `timestamp` greater than any previous call.
    """
    def __init__(self) -> None:
        self.accounts = {"global": Account("global", 2**32-1)}

    # -------------------- Level 1 --------------------
    def add_file(self, timestamp: int, name: str, size: int) -> bool:
        """
        Create a new file called `name` with the given `size` in the
        ownerless (global) namespace.
        Return True if created, or False if a file with `name` already
        exists.
        """
        if name in self.accounts["global"].files:
            return False
        
        file = File(timestamp, name, size)
        self.accounts["global"].files[name] = file
        return True

    def get_file_size(self, timestamp: int, name: str) -> int | None:
        """
        Return the current size of `name`, or None if it doesn't exist.
        """
        if name in self.accounts["global"].files:
            file = self.accounts["global"].files[name]
            return file.size
        return None

    def delete_file(self, timestamp: int, name: str) -> int | None:
        """
        Delete `name` and return the size it had, or None if it doesn't
        exist.
        """
        if name in self.accounts["global"].files:
            file = self.accounts["global"].files.pop(name)
            return file.size
        return None

    # -------------------- Level 2 --------------------
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
        ranked_list = []
        for id in self.accounts:
            for name in self.accounts[id].files:
                file = self.accounts[id].files[name]
                if name.startswith(prefix):
                    ranked_list.append((name, file.size))

        ranked_list = sorted(ranked_list, key= lambda item: (-item[1], item[0]))

        return [f"{ranked_list[index][0]}({ranked_list[index][1]})" for index in range(min(len(ranked_list), n)) ]

    # -------------------- Level 3 --------------------
    def add_user(self, timestamp: int, user_id: str, capacity: int) -> bool:
        """
        Create a new user with the given total storage `capacity`.
        Return True if created, or False if `user_id` already exists.
        """
        if user_id in self.accounts:
            return False
        account = Account(user_id, capacity)
        self.accounts[user_id] = account
        return True

    def add_file_by(self, timestamp: int, user_id: str, name: str, size: int) -> int | None:
        """
        Add a file called `name` owned by `user_id`. A file name only needs
        to be unique within that user's own namespace.
        Return the user's remaining capacity (`capacity - total used`) after
        adding the file, or None if: the user does not exist, the user
        already owns a file called `name`, or adding the file would exceed
        the user's capacity.
        """
        if user_id in self.accounts:
            account = self.accounts[user_id]
            if (name not in account.files and
                account.capacity >= account.used_capacity + size):
                file = File(timestamp, name, size)
                account.files[name] = file
                account.used_capacity += size
                return account.capacity - account.used_capacity
        return None

    def delete_file_by(self, timestamp: int, user_id: str, name: str) -> int | None:
        """
        Remove `user_id`'s file called `name`.
        Return the user's remaining capacity after the removal, or None if
        the user does not exist or does not own a file called `name`.
        """
        if user_id in self.accounts:
            account = self.accounts[user_id]
            if (name in account.files):
                file = account.files.pop(name)
                account.used_capacity -= file.size
                return account.capacity - account.used_capacity
        return None

    # -------------------- Level 4 --------------------
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
        if (user_id_1 == user_id_2 or
            user_id_1 not in self.accounts or
            user_id_2 not in self.accounts):
            return False
        account1 = self.accounts[user_id_1]
        account2 = self.accounts.pop(user_id_2)
        account1.capacity += account2.capacity
        for file in account2.files:
            name = file
            while True:
                if name in account1.files:
                    name = name + " (merged)"
                    continue
                break
            
            self.add_file_by(timestamp, user_id_1, name, account2.files[file].size)

        return True

    def backup_user(self, timestamp: int, user_id: str) -> int | None:
        """
        Save a snapshot of `user_id`'s current capacity and full set of
        owned files. A later call to `backup_user` for the same user
        overwrites the previous snapshot.
        Return the number of files captured in the snapshot, or None if the
        user does not exist.
        """
        if user_id not in self.accounts:
            return None
        size = 0
        file_counter = 0
        account = Account(name= user_id,
                          capacity= self.accounts[user_id].capacity)
        for file in self.accounts[user_id].files:
            size += self.accounts[user_id].files[file].size
            account.files[file] = self.accounts[user_id].files[file]
            file_counter += 1
        account.used_capacity = size
        self.accounts[user_id].snapshot = account
        self.accounts[user_id].hasSnapshot = True
        return file_counter

    def restore_user(self, timestamp: int, user_id: str) -> int | None:
        """
        Restore `user_id`'s capacity and files to the most recent snapshot
        taken by `backup_user`, discarding any changes made since (including
        files or capacity gained through a later `merge_user`).
        Return the number of files restored, or None if the user does not
        exist or has no snapshot.
        """
        if user_id not in self.accounts:
            return None
        if self.accounts[user_id].hasSnapshot:
            self.accounts[user_id] = self.accounts[user_id].snapshot
            return len(self.accounts[user_id].files)
        return None
