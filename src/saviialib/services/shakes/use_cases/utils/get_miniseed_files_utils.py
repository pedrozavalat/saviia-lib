from typing import Dict, List, Any


def parse_downloaded_metadata(responses: List[Any]) -> Dict[str, Any]:
    return {
        x["rs_name"]: {
            "destination_path": x["destination_path"],
            "total_files": x["total_files"],
        }
        for x in responses
    }
