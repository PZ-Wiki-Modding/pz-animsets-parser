"""
Parse the media/AnimSets/player/actions files to extract available actions 
to use in the API or Scripts
"""

import os, json, yaml
from pathlib import Path
import xml.etree.ElementTree as ET

from util import AnimSets
from util.AnimNode import AnimNode, ConditionElement, EventElement

CONDITIONS_DOC = Path("")
OUTPUT_ACTIONS = Path("out/performing_actions.json")
OUTPUT_CONDITIONS = Path("out/conditions.json")
OUTPUT_EVENTS = Path("out/events.json")

INPUT_DATA = Path("data")

# values if None
_default_values = {
    EventElement.NAME: "",
    EventElement.VALUE: "",
}

def get_elements(child: ET.Element, element_class) -> dict[str, str]:
    elements = {}
    is_test = False
    for subchild in child:
        tag = subchild.tag
        elementTag = element_class.get_tag(tag)
        if elementTag is None:
            print(f"Warning: Unknown element tag '{tag}' in file {child.tag}. Skipping this element.")
            continue
        text = subchild.text
        if text is None and elementTag in _default_values:
            text = _default_values[elementTag]
        elements[elementTag] = text

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
    try:
        tree = ET.parse(action_file)
    except ET.ParseError as e:
        print(f"Error parsing XML file {action_file}: {e}")
        return None
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

def retrieve_extra_data(output_file: Path, data: dict):
    extra_data_file = INPUT_DATA / (output_file.stem + ".yaml")
    if not extra_data_file.is_file():
        return
    print(f"Retrieving extra data from {extra_data_file}")
    with open(extra_data_file, "r") as f:
        extra_data = yaml.safe_load(f)

    for key, value in extra_data.items():
        if key not in data:
            raise KeyError(f"Key '{key}' from extra data file {extra_data_file} not found in main data.")
        else:
            data[key].update(value)

def main():
    animsets_path = AnimSets.get_animsets_path()

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
        try:
            tree = ET.parse(action_file)
        except ET.ParseError as e:
            print(f"Error parsing XML file {action_file}: {e}")
            continue
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

    to_out = {
        OUTPUT_ACTIONS: out_actions,
        OUTPUT_CONDITIONS: out_conditions,
        OUTPUT_EVENTS: out_events
    }

    for output_file, data in to_out.items():
        retrieve_extra_data(output_file, data)
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()