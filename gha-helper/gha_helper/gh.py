import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class CICDInputError(Exception):
    pass


Unset = object()


def _escape_data(s) -> str:
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(s) -> str:
    return (
        str(s)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


class Input:
    def get(self, name: str, default=Unset):
        env = os.getenv(name, default)

        if env is Unset:
            raise CICDInputError(f"Cannot find input {name}. Previous jobs have probably failed.")

        return env

    def get_timestamp(self, name: str) -> datetime:
        env = os.environ[name]

        try:
            return datetime.fromtimestamp(int(env), tz=timezone.utc)
        except:
            return datetime.strptime(env, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    def get_json(self, name: str, default=Unset):
        env = os.getenv(name)

        if not env:
            if default is Unset:
                raise CICDInputError(f"Cannot find input {name}. Previous jobs have probably failed.")
            else:
                return default

        return json.loads(env)


class Output:
    def save(self, name: str, value: Any):
        with open(os.environ["GITHUB_OUTPUT"], "w+") as f:
            f.write(f"{name}={value}\n")

    def save_json(self, name: str, value: Any):
        data = json.dumps(value, separators=(",", ":"))
        with open(os.environ["GITHUB_OUTPUT"], "w+") as f:
            f.write(f"{name}={data}\n")


class Annotation:
    def error(
        self,
        message: str,
        file: Optional[Path | str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        self._print("error", message, file, line, col)

    def warning(
        self,
        message: str,
        file: Optional[Path | str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        self._print("warning", message, file, line, col)

    def notice(
        self,
        message: str,
        file: Optional[Path | str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        self._print("notice", message, file, line, col)

    def _print(
        self,
        level: str,
        message: str,
        file: Optional[Path | str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        if file is not None:
            print(f"In file {file}:{line}:{col}:")

        props = []

        if file is not None:
            props.append(f"file={_escape_property(file)}")

        if line is not None:
            props.append(f"line={line}")

        if col is not None:
            props.append(f"col={col}")

        props_str = ",".join(props)
        if props_str:
            props_str = " " + props_str

        print(f"::{level}{props_str}::{_escape_data(message)}")


input = Input()
output = Output()
annotation = Annotation()
