# Remove all files and folders inside %APPDATA%\Code\User\workspaceStorage.
import os
import shutil


def delete_copilot_cache() -> None:
    cache_path = os.path.expandvars(r"%APPDATA%\Code\User\workspaceStorage")

    if not os.path.isdir(cache_path):
        print(f"No Copilot cache found at: {cache_path}")
        return

    for name in os.listdir(cache_path):
        target_path = os.path.join(cache_path, name)

        try:
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        except OSError as error:
            print(f"Failed to delete: {target_path}")
            print(error)

    print(f"Cleared Copilot cache contents at: {cache_path}")


if __name__ == "__main__":
    delete_copilot_cache()