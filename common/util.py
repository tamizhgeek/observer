from urllib.parse import urlparse


def url_to_topic(url: str, check_name: str = "http_check") -> str:
    cleaned_url = urlparse(url).hostname.replace(".", "__")
    return f"observer.{cleaned_url}.{check_name}"
