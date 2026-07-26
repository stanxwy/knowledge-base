import json
from app.workflows.ingestion.nodes.node_entry import NodeEntry

if __name__ == "__main__":
    init_state = {"import_file_path": "./test_data/kb/B3-211H.pdf"}
    node_entry = NodeEntry()
    result = node_entry(init_state)
    print(json.dumps(result, ensure_ascii=False, indent=4))

"""
{
    "is_pdf_read_enabled": true,
    "pdf_path": "./test_data/kb/B3-211H.pdf",
    "file_title": "B3-211H"
}
"""