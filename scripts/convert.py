"""
Converts all XML files in the AnimSets directory to JSON format
"""

import xmltodict, json
from pathlib import Path

from util import AnimSets


def convert_xml_to_json(output_dir: Path):
    animsets_path = AnimSets.get_animsets_path()

    for action_file in animsets_path.rglob("*.xml"):
        print(action_file)

        try:
            with open(action_file, "r") as f:
                xml_content = f.read()
                o = xmltodict.parse(xml_content)
                json_content = json.dumps(o, indent=4)
                # print(json_content)
        except Exception as e:
            print(f"Error processing file {action_file}: {e}")
            continue

        # retrieve relative path to the animsets directory
        relative_path = action_file.relative_to(animsets_path)
        print(relative_path)

        output_file = output_dir / relative_path.with_suffix(".json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(json_content)

if __name__ == "__main__":
    OUTPUT = Path("out/json")
    convert_xml_to_json(OUTPUT)