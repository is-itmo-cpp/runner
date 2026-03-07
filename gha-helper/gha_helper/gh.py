import json
import os
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo


class CICDInputError(Exception): pass


Unset = object()


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
        env = os.getenv(name,)
                                                                                    
        if not env:                                                             
            if default is Unset:                                                    
                raise CICDInputError(f"Cannot find input {name}. Previous jobs have probably failed.")
            else:
                return default

        return json.loads(env)


class Output:
    def save(self, name: str, value: Any):
        with open(os.environ["GITHUB_OUTPUT"], "w+") as f:
            f.write(f"{name}={value}")

    def save_json(self, name: str, value: Any):
        data = json.dumps(value, separators=(',', ':'))
        with open(os.environ["GITHUB_OUTPUT"], "w+") as f:
            f.write(f"{name}={data}")


input = Input()
output = Output()
