from cfg4py import config_server, create_config
import fire


def build(config_dir: str):
    import os
    import sys
    if not os.path.exists(config_dir):
        print(f"path {config_dir} not exists")
        sys.exit(-1)

    count = 0
    for f in os.listdir(config_dir):
        if f.startswith("default") or f.startswith("dev") or f.startswith("test") or f.startswith("production"):
            print(f"found {f}")
            count += 1

    if count > 0:
        print(f"{count} files found in total")
    else:
        print("the folder contains no valid configuration files")
        sys.exit(-1)

    try:
        create_config(config_dir)
        sys.path.insert(0, config_dir)
        # noinspection PyUnresolvedReferences
        from cfg4py_auto_gen import Config
        print(f"Config file is built with success and saved at {os.path.join(config_dir, 'cfg4py_auto_gen')}")
    except Exception as e:
        print(e)
        print("Config file built failure.")


def main():
    fire.Fire({
        "build":         build,
        "config_server": config_server
    })
