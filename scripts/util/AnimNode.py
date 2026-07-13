from enum import StrEnum

class AnimNode(StrEnum):
    CONDITION = "m_Conditions"
    EVENT = "m_Events"

    # attributes
    EXTENDS = "x_extends"

class _Element(StrEnum):
    @classmethod
    def get_tag(cls, tag: str) -> "_Element | None":
        """Checks if the provided tag is a valid element of the enum."""
        for element in cls:
            if tag == element.value:
                return element
        return None

class ConditionElement(_Element):
    NAME = "m_Name"
    TYPE = "m_Type"
    VALUE = "m_Value"
    INT = "m_IntValue"
    FLOAT = "m_FloatValue"
    BOOL = "m_BoolValue"
    STRING = "m_StringValue"

class EventElement(_Element):
    NAME = "m_EventName"
    TIME = "m_Time"
    TIME_PC = "m_TimePc"
    VALUE = "m_ParameterValue"