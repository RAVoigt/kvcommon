import requests

from kvcommon.logger import get_logger

LOG = get_logger("kvc-k8s")


def get_project_id() -> str:
    """Fetch GCP Project ID from the metadata server."""
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
    headers = {"Metadata-Flavor": "Google"}

    try:
        response = requests.get(metadata_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as ex:
        LOG.error(f"Unexpected error fetching GCP project ID from metadata server: {ex}")
        # return None
        raise
