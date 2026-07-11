from typing import List
import os
import tempfile

SUPPORTED_IDES = ["PyCharm", "VSCode", "SublimeText"]

def get_supported_ides() -> List[str]:
    """
    Returns a list of supported IDEs for integration.
    """
    return SUPPORTED_IDES

def integrate_with_ide(ide_name: str) -> None:
    """
    Integrates the CodeFlowSecurityAgent with the specified IDE.

    :param ide_name: The name of the IDE to integrate with.
    :raises ValueError: If the IDE is not supported.
    """
    if ide_name not in SUPPORTED_IDES:
        raise ValueError(f"IDE '{ide_name}' is not supported. Supported IDEs are: {', '.join(SUPPORTED_IDES)}")

    # Integration logic specific to each IDE
    if ide_name == "PyCharm":
        _integrate_with_pycharm()
    elif ide_name == "VSCode":
        _integrate_with_vscode()
    elif ide_name == "SublimeText":
        _integrate_with_sublimetext()

def _integrate_with_pycharm() -> None:
    """
    Internal function to handle PyCharm integration.
    """
    try:
        # Example: Write configuration to a temporary file
        fd, path = tempfile.mkstemp(suffix=".xml")
        with os.fdopen(fd, 'w') as tmp:
            tmp.write("<component name=\"InspectionProjectProfileManager\">\n")
            tmp.write("  <profile version=\"1.0\">\n")
            tmp.write("    <option name=\"myOption\" value=\"true\" />\n")
            tmp.write("  </profile>\n")
            tmp.write("</component>\n")
        
        # Here you would add the actual steps to integrate with PyCharm
        print(f"Integration with PyCharm configured. Configuration file: {path}")
    except Exception as e:
        print(f"Error during PyCharm integration: {str(e)}")

def _integrate_with_vscode() -> None:
    """
    Internal function to handle VSCode integration.
    """
    try:
        # Example: Write configuration to a temporary file
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, 'w') as tmp:
            tmp.write("{\n")
            tmp.write("  \"version\": 1,\n")
            tmp.write("  \"settings\": {\n")
            tmp.write("    \"mySetting\": true\n")
            tmp.write("  }\n")
            tmp.write("}\n")
        
        # Here you would add the actual steps to integrate with VSCode
        print(f"Integration with VSCode configured. Configuration file: {path}")
    except Exception as e:
        print(f"Error during VSCode integration: {str(e)}")

def _integrate_with_sublimetext() -> None:
    """
    Internal function to handle SublimeText integration.
    """
    try:
        # Example: Write configuration to a temporary file
        fd, path = tempfile.mkstemp(suffix=".sublime-settings")
        with os.fdopen(fd, 'w') as tmp:
            tmp.write("{\n")
            tmp.write("  \"my_setting\": true\n")
            tmp.write("}\n")
        
        # Here you would add the actual steps to integrate with SublimeText
        print(f"Integration with SublimeText configured. Configuration file: {path}")
    except Exception as e:
        print(f"Error during SublimeText integration: {str(e)}")