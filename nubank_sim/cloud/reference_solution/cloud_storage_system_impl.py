from cloud.cloud_storage_system import CloudStorageSystem


class CloudStorageSystemImpl(CloudStorageSystem):

    def __init__(self):
        # files: (owner, name) -> size. owner is None for the ownerless
        # namespace used by add_file/get_file_size/delete_file.
        self.files = {}
        # users: user_id -> {"capacity": int, "used": int}
        self.users = {}
        # backups: user_id -> {"capacity": int, "used": int, "files": {name: size}}
        self.backups = {}

    # -------------------- Level 1 --------------------
    def add_file(self, timestamp: int, name: str, size: int) -> bool:
        key = (None, name)
        if key in self.files:
            return False
        self.files[key] = size
        return True

    def get_file_size(self, timestamp: int, name: str) -> int | None:
        return self.files.get((None, name))

    def delete_file(self, timestamp: int, name: str) -> int | None:
        key = (None, name)
        if key not in self.files:
            return None
        return self.files.pop(key)

    # -------------------- Level 2 --------------------
    def get_n_largest(self, timestamp: int, prefix: str, n: int) -> list[str]:
        matches = [
            (name, size)
            for (owner, name), size in self.files.items()
            if name.startswith(prefix)
        ]
        matches.sort(key=lambda item: (-item[1], item[0]))
        if n > len(matches):
            n = len(matches)
        return [f"{name}({size})" for name, size in matches[:n]]

    # -------------------- Level 3 --------------------
    def add_user(self, timestamp: int, user_id: str, capacity: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = {"capacity": capacity, "used": 0}
        return True

    def add_file_by(self, timestamp: int, user_id: str, name: str, size: int) -> int | None:
        if user_id not in self.users:
            return None
        key = (user_id, name)
        if key in self.files:
            return None
        user = self.users[user_id]
        if user["used"] + size > user["capacity"]:
            return None
        self.files[key] = size
        user["used"] += size
        return user["capacity"] - user["used"]

    def delete_file_by(self, timestamp: int, user_id: str, name: str) -> int | None:
        if user_id not in self.users:
            return None
        key = (user_id, name)
        if key not in self.files:
            return None
        size = self.files.pop(key)
        user = self.users[user_id]
        user["used"] -= size
        return user["capacity"] - user["used"]

    # -------------------- Level 4 --------------------
    def merge_user(self, timestamp: int, user_id_1: str, user_id_2: str) -> bool:
        if (
            user_id_1 == user_id_2
            or user_id_1 not in self.users
            or user_id_2 not in self.users
        ):
            return False

        u1 = self.users[user_id_1]
        u2 = self.users[user_id_2]
        u1["capacity"] += u2["capacity"]
        u1["used"] += u2["used"]

        to_move = [
            (name, size)
            for (owner, name), size in list(self.files.items())
            if owner == user_id_2
        ]
        for name, size in to_move:
            del self.files[(user_id_2, name)]
            new_name = name
            while (user_id_1, new_name) in self.files:
                new_name = f"{new_name} (merged)"
            self.files[(user_id_1, new_name)] = size

        del self.users[user_id_2]
        self.backups.pop(user_id_2, None)
        return True

    def backup_user(self, timestamp: int, user_id: str) -> int | None:
        if user_id not in self.users:
            return None
        user = self.users[user_id]
        files_snapshot = {
            name: size
            for (owner, name), size in self.files.items()
            if owner == user_id
        }
        self.backups[user_id] = {
            "capacity": user["capacity"],
            "used": user["used"],
            "files": files_snapshot,
        }
        return len(files_snapshot)

    def restore_user(self, timestamp: int, user_id: str) -> int | None:
        if user_id not in self.users or user_id not in self.backups:
            return None
        backup = self.backups[user_id]

        current_keys = [
            (owner, name) for (owner, name) in self.files.keys() if owner == user_id
        ]
        for key in current_keys:
            del self.files[key]

        for name, size in backup["files"].items():
            self.files[(user_id, name)] = size

        self.users[user_id]["capacity"] = backup["capacity"]
        self.users[user_id]["used"] = backup["used"]
        return len(backup["files"])

    # TODO: implement interface methods here
    # Level 1: add_file, get_file_size, delete_file
    # Level 2: get_n_largest
    # Level 3: add_user, add_file_by, delete_file_by
    # Level 4: merge_user, backup_user, restore_user
