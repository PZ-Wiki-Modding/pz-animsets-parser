"""
Parse the media/AnimSets/player/actions files to extract available actions 
to use in the API or Scripts
"""

import os, json
from pathlib import Path
import xml.etree.ElementTree as ET

from util import AnimSets
from util.AnimNode import ANIM_NODE


OUTPUT = Path("out/performing_actions.json")



if __name__ == "__main__":
    animsets_path = AnimSets.get_player_animset_path()

    actions_path = animsets_path / "actions"
    if not actions_path.is_dir():
        raise NotADirectoryError(f"The expected actions directory does not exist: {actions_path}.")
    
    out = []

    anim_nodes = sorted(actions_path.glob("*.xml"), key=lambda p: p.name.lower())
    for action_file in anim_nodes:
        print(f"Found action file: {action_file.name}")

        tree = ET.parse(action_file)
        root = tree.getroot()
        # print(root.tag)
        # print(root.attrib)

        for child in root:
            if child.tag == ANIM_NODE.CONDITION:
                properties = {}
                for subchild in child:
                    match subchild.tag:
                        case ANIM_NODE.NAME:
                            properties["name"] = subchild.text
                        case ANIM_NODE.TYPE:
                            properties["type"] = subchild.text
                        case ANIM_NODE.VALUE:
                            properties["value"] = subchild.text

                # find PerformingAction conditions
                if properties.get("name", "") != "PerformingAction":
                    continue

                # only handle cases containing name, type and value
                # other cases are abnormal
                if len(properties) != 3:
                    print(f"Warning: Incomplete properties for condition in file {action_file.name}: {properties}")
                    continue

                out.append({
                    "file": action_file.name,
                    "action": properties["value"]
                })

    with open(OUTPUT, "w") as f:
        json.dump(out, f, indent=4)