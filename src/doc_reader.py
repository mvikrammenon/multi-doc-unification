import os

def read_component_docs(component_name: str) -> dict[str, str]:
    """
    Scans the data/ directory for component documentation files.

    Args:
        component_name: The name of the component (e.g., "component1").

    Returns:
        A dictionary where keys are source names (e.g., "source1")
        and values are the content of the respective documentation file.
    """
    data_dir = "data"
    component_docs = {}

    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        return component_docs

    for source_name in os.listdir(data_dir):
        source_path = os.path.join(data_dir, source_name)
        if os.path.isdir(source_path):
            component_file_name = f"{component_name}.txt"
            component_file_path = os.path.join(source_path, component_file_name)
            try:
                with open(component_file_path, 'r') as f:
                    content = f.read()
                component_docs[source_name] = content
            except FileNotFoundError:
                # If the component file doesn't exist in this source, skip it.
                pass
    return component_docs
