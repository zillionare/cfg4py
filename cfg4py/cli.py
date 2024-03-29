import logging
import os
import sys
from typing import Optional

import fire
from ruamel.yaml import YAML

from cfg4py import enable_logging, envar, init

enable_logging()


class Command:
    def __init__(self):
        self.resource_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "resources/")
        )
        self.yaml = YAML(typ="safe")  # default, if not specfied, is 'rt' (round-trip)
        self.yaml.default_flow_style = False

        with open(
            os.path.join(self.resource_path, "template.yaml"), "r", encoding="utf-8"
        ) as f:
            self.templates = self.yaml.load(f)

        self.transformed = self._transform()

    def build(self, config_dir: str):
        """Compile configuration files into python script, which is used by IDE's
        auto-complete function

        Args:
            config_dir: The folder where your configuration files located

        Returns:

        """
        if not os.path.exists(config_dir):
            print(f"path {config_dir} not exists")
            sys.exit(-1)

        count = 0
        for f in os.listdir(config_dir):
            if (
                f.startswith("default")
                or f.startswith("dev")
                or f.startswith("test")
                or f.startswith("production")
            ):
                print(f"found {f}")
                count += 1

        if count > 0:
            print(f"{count} files found in total")
        else:
            print("the folder contains no valid configuration files")
            sys.exit(-1)

        try:
            init(config_dir)
            sys.path.insert(0, config_dir)
            from schema import Config  # type: ignore # noqa

            output_file = f"{os.path.join(config_dir, 'schema')}"
            msg = f"Config file is built with success and saved at {output_file}"
            print(msg)
        except Exception as e:  # pragma: no cover
            logging.exception(e)
            print("Config file built failure.")

    def _choose_dest_dir(self, dst):
        if dst is None:
            dst = input("Where should I save configuration files?\n")

        if os.path.exists(dst):
            for f in os.listdir(dst):
                msg = f"The folder already contains {f}, please choose clean one."

                if f in ["defaults.yaml", "dev.yaml", "test.yaml", "production.yaml"]:
                    print(msg)
                    return None
            return dst
        else:
            create = input("Path not exists, create('Q' to exit)? [Y/n]")
            if create.upper() == "Y":
                os.makedirs(dst, exist_ok=True)
                return dst
            elif create.upper() == "Q":
                sys.exit(-1)
            else:
                return None

    def scaffold(self, dst: Optional[str]):
        """Creates initial configuration files based on our choices.
        Args:
            dst:

        Returns:

        """
        print("Creating a configuration boilerplate:")
        dst = self._choose_dest_dir(dst)
        while dst is None:
            dst = self._choose_dest_dir(dst)

        yaml = YAML(typ="safe")  # default, if not specfied, is 'rt' (round-trip)
        with open(
            os.path.join(self.resource_path, "template.yaml"), "r", encoding="utf-8"
        ) as f:
            templates = yaml.load(f)

        print("Which flavors do you want?")
        print("-" * 20)
        prompt = """
        0  - console + rotating file logging
        10 - redis/redis-py (gh://andymccurdy/redis-py)
        11 - redis/aioredis (gh://aio-libs/aioredis)
        20 - mysql/PyMySQL (gh://PyMySQL/PyMySQL)
        30 - postgres/asyncpg (gh://MagicStack/asyncpg)
        31 - postgres/psycopg2 (gh://psycopg/psycopg2)
        40 - mq/pika (gh://pika/pika)
        50 - mongodb/pymongo (gh://mongodb/mongo-python-driver)
        """
        print(prompt)
        chooses = input(
            "Please choose flavors by index, separated each by a comma(,):\n"
        )
        flavors = {}
        mapping = {
            "0": "logging",
            "1": "redis",
            "2": "mysql",
            "3": "postgres",
            "4": "mq",
            "5": "mongodb",
        }
        for index in chooses.strip(" ").split(","):
            if index == "0":
                flavors["logging"] = templates["logging"]
                continue

            try:
                major = mapping[index[0]]
                minor = int(index[1])
                flavors[major] = list(templates[major][minor].values())[0]
            except (ValueError, KeyError):
                print(f"Wrong index {index}, skipped.")
                continue

        with open(os.path.join(dst, "defaults.yaml"), "w", encoding="utf-8") as f:
            f.writelines(
                "#auto generated by Cfg4Py: https://github.com/jieyu-tech/cfg4py\n"
            )
            yaml.dump(flavors, f)

        print(f"Cfg4Py has generated the following files under {dst}:")
        print("defaults.yaml")
        for name in ["dev.yaml", "test.yaml", "production.yaml"]:
            with open(os.path.join(dst, name), "w", encoding="utf8") as f:
                f.writelines(
                    "#auto generated by Cfg4Py: https://github.com/jieyu-tech/cfg4py\n"
                )
                print(name)

        with open(os.path.join(dst, "defaults.yaml"), "r", encoding="utf-8") as f:
            print("Content in defaults.yaml")
            for line in f.readlines():
                print(line.replace("\n", ""))

    def _show_supported_config(self):
        print("Support the following configurations:")
        for key in self.templates.keys():
            item = self.templates.get(key)
            if isinstance(item, dict):
                print(f"  {key}")
            elif isinstance(item, list):
                sub_keys = []
                for sub_item in item:
                    sub_keys.append(f"{key}/{list(sub_item.keys())[0]}")
                print(f"  {key}: {', '.join(sub_keys)}")

    def _transform(self):
        transformed = {}
        for key in self.templates:
            if isinstance(self.templates[key], dict):
                transformed[key] = self.templates[key]
            elif isinstance(self.templates[key], list):
                for item in self.templates[key]:
                    item_key = list(item.keys())[0]
                    transformed[f"{key}/{item_key}"] = item

        return transformed

    def hint(self, what: str = None, usage: bool = False):
        """show a cheat sheet for configurations.
        for example:
            cfg4py hint mysql
        this will print how to configure PyMySQL
        :param what
        :param usage
        """

        if what is None or (
            (what not in self.templates) and what not in self.transformed
        ):
            return self._show_supported_config()

        usage_key = f"{what}_usage"

        if usage_key in self.templates and usage:
            print("Usage:", self.templates.get(usage_key))

        if what in self.templates:
            self.yaml.dump(self.templates[what], sys.stdout)

        if usage_key in self.transformed and usage:
            print("Usage:", self.transformed.get(usage_key))

        if what in self.transformed:
            self.yaml.dump(self.transformed[what], sys.stdout)

    def set_server_role(self):
        print("please add the following line into your .bashrc:\n")
        print(f"export {envar}=DEV\n")
        msg = "You need to change DEV to TEST | PRODUCTION according to its actual role\
         accordingly"
        print(msg)

    def version(self):
        from cfg4py import __version__

        print(
            "Easy config module support code complete, cascading design and apative deployment"
        )
        print(f"version: {__version__}")


def main():
    cmd = Command()  # pragma: no cover
    fire.Fire(
        {  # pragma: no cover
            "build": cmd.build,
            "scaffold": cmd.scaffold,
            "hint": cmd.hint,
            "set_server_role": cmd.set_server_role,
            "--version": cmd.version,
            "-v": cmd.version(),
        }
    )


if __name__ == "__main__":
    main()
