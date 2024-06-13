"""Workaround for https://github.com/OpenAPITools/openapi-generator/issues/13302

Comes from
https://github.com/OpenAPITools/openapi-generator/issues/13302#issuecomment-1804867478
"""

import requests
import json
import sys


def main():
    with requests.Session() as session:
        result = session.get(sys.argv[1])
        if (result.status_code != 200):
            print("ERROR: status_code=" + result.status_code)
            return
        data = json.loads(result.text)
        if (("components" in data) and ("schemas" in data["components"])
            and ("ValidationError" in data["components"]["schemas"])
            and ("properties" in data["components"]["schemas"]["ValidationError"])
                and ("loc" in data["components"]["schemas"]["ValidationError"]["properties"])
                and ("items" in data["components"]["schemas"]["ValidationError"]["properties"]["loc"])):
            data["components"]["schemas"]["ValidationError"]["properties"]["loc"]["items"] = {"type": "string"}
        with open('./openapi.json', 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()