"""
Parse the media/AnimSets/player/actions files to extract available actions 
to use in the API or Scripts
"""

import os, json
from pathlib import Path
import xml.etree.ElementTree as ET

from util import AnimSets
from util.AnimNode import AnimNode, ConditionElement, EventElement

CONDITIONS_DOC = Path("")
OUTPUT_ACTIONS = Path("out/performing_actions.json")
OUTPUT_CONDITIONS = Path("out/conditions.json")
OUTPUT_EVENTS = Path("out/events.json")

def get_elements(child: ET.Element, element_class) -> dict[str, str]:
    elements = {}
    for subchild in child:
        tag = subchild.tag
        elementTag = element_class.get_tag(tag)
        if elementTag is None:
            print(f"Warning: Unknown element tag '{tag}' in file {child.tag}. Skipping this element.")
            continue
        elements[elementTag] = subchild.text
    return elements

def get_extends_path(action_file: Path, root: ET.Element) -> Path | None:
    attributes = root.attrib
    extends = attributes.get(AnimNode.EXTENDS, None)
    if extends is not None:
        return action_file.parent / extends
    return None

def get_action(action_file) -> dict[str, str] | None:
    """
    Retrieves values of blocks with such structure:
    ```xml
    <m_Conditions>
		<m_Name>PerformingAction</m_Name>
		<m_Type>STRING</m_Type>
		<m_Value>Loot</m_Value>
	</m_Conditions>
    ```
    """
    tree = ET.parse(action_file)
    root = tree.getroot()
    extends_path = get_extends_path(action_file, root)

    final_elements = None
    for child in root:
        if child.tag != AnimNode.CONDITION:
            continue
        elements = get_elements(child, ConditionElement)
        
        # check if performing action
        if elements.get(ConditionElement.NAME, "") != "PerformingAction":
            continue

        # duplicate action, weird
        if final_elements is not None:
            print(f"Warning: Duplicate PerformingAction conditions in file {action_file.name}: {elements}")
            continue

        # find name
        name = elements.get(ConditionElement.NAME, None)
        if name is None:
            # find in extends
            if extends_path is None or not extends_path.is_file():
                continue

            # access name
            elements_extend = get_action(extends_path)
            if elements_extend is not None:
                extends_name = elements_extend[ConditionElement.NAME]
                elements[ConditionElement.NAME] = extends_name
            else:
                print(f"Warning: Could not find PerformingAction name in extends file {extends_path.name} for file {action_file.name}")
                continue
        
        final_elements = elements

    return final_elements

def main():
    animsets_path = AnimSets.get_player_animset_path()

    actions_path = animsets_path# / "actions"
    if not actions_path.is_dir():
        raise NotADirectoryError(f"The expected actions directory does not exist: {actions_path}.")
    
    out_actions = []
    out_conditions = {}
    out_events = {}

    anim_nodes = sorted(actions_path.rglob("*.xml"), key=lambda p: p.name.lower())
    for action_file in anim_nodes:
        # find PerformingAction condition
        action = get_action(action_file)
        if action is not None:
            out_actions.append({
                "file": action_file.name,
                "action": action[ConditionElement.VALUE]
            })

        # parse conditions in general
        tree = ET.parse(action_file)
        root = tree.getroot()

        for child in root:
            if child.tag == AnimNode.CONDITION:
                elements = get_elements(child, ConditionElement)

                # store possible value
                name = elements.get(ConditionElement.NAME, None)
                value = elements.get(ConditionElement.VALUE, None)
                if name is None or value is None:
                    continue

                # store vanilla value
                vanillaValues = out_conditions.setdefault(name, {}).setdefault("vanillaValues", [])
                if value not in vanillaValues:
                    vanillaValues.append(value)
            elif child.tag == AnimNode.EVENT:
                elements = get_elements(child, EventElement)

                # store possible value
                name = elements.get(EventElement.NAME, None)
                value = elements.get(EventElement.VALUE, None)
                if name is None or value is None:
                    continue

                # store vanilla value
                vanillaValues = out_events.setdefault(name, {}).setdefault("vanillaValues", [])
                if value not in vanillaValues:
                    vanillaValues.append(value)


    with open(OUTPUT_ACTIONS, "w") as f:
        json.dump(out_actions, f, indent=4, sort_keys=True)

    with open(OUTPUT_CONDITIONS, "w") as f:
        json.dump(out_conditions, f, indent=4, sort_keys=True)

    with open(OUTPUT_EVENTS, "w") as f:
        json.dump(out_events, f, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()