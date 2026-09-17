from datetime import datetime

from langchain_core.tools import tool
from langchain_community.tools import (
    DuckDuckGoSearchRun,
    WikipediaQueryRun,
)
from langchain_community.utilities import WikipediaAPIWrapper

@tool
def calculator_tool(a: float, b: float, operation: str) -> float:
    """Perform a basic calculation."""

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            return 0
        return a / b

    else:
        return 0
    
search_tool = DuckDuckGoSearchRun()    

wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=2,
        doc_content_chars_max=4000,
    )
)


# =========================
# UNIT CONVERSION
# =========================

@tool
def unit_conversion(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """Convert common units of length, weight, and temperature."""

    conversions = {
        # length → meters
        "m": 1,
        "km": 1000,
        "cm": 0.01,
        "mm": 0.001,
        "mile": 1609.344,
        "ft": 0.3048,
        "inch": 0.0254,

        # weight → kilograms
        "kg": 1,
        "g": 0.001,
        "lb": 0.45359237,
        "lbs": 0.45359237,
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # Temperature
    if from_unit in ["c", "celsius"] and to_unit in ["f", "fahrenheit"]:
        return (value * 9 / 5) + 32

    if from_unit in ["f", "fahrenheit"] and to_unit in ["c", "celsius"]:
        return (value - 32) * 5 / 9

    # Normal conversion
    if from_unit in conversions and to_unit in conversions:

        return (
            value * conversions[from_unit]
            / conversions[to_unit]
        )

    raise ValueError(
        f"Unsupported conversion: {from_unit} → {to_unit}"
    )


@tool
def current_datetime() -> str:
    """Return the current local date and time."""

    return datetime.now().strftime(
        "%A, %d %B %Y, %I:%M:%S %p"
    )

