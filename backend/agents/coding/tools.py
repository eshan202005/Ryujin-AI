from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.utilities import PythonREPL


# --------------------------------------------------
# Python Execution Tool
# --------------------------------------------------

python_repl = PythonREPL()


@tool
def python_execution(code: str) -> str:
    """
    Execute Python code and return the output.

    Use this to verify Python code, test logic,
    or investigate Python errors.
    """

    return python_repl.run(code)


# --------------------------------------------------
# Test Execution Tool
# --------------------------------------------------

@tool
def run_tests(test_command: str) -> str:
    """
    Run a test command and return the test output.

    Use this to verify whether code passes its tests.
    """

    import subprocess

    result = subprocess.run(
        test_command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return (
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}\n"
        f"RETURN CODE: {result.returncode}"
    )


# --------------------------------------------------
# Web Search Tool
# --------------------------------------------------

search_tool = DuckDuckGoSearchRun()