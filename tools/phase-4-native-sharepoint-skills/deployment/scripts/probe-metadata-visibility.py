"""
Phase 4 Metadata Exposure Probe Helper
Generates structured query payloads for testing custom agent metadata exposure.
"""
import json

TEST_FIELDS = [
    "TopicID",
    "PublicationOrder",
    "TopicContentSHA256",
    "Status",
    "ReviewDate",
    "TransitionAction",
    "TransitionTarget"
]

def generate_probe_queries(topic_filename: str) -> list[dict]:
    queries = []
    for field in TEST_FIELDS:
        queries.append({
            "field": field,
            "target_topic": topic_filename,
            "prompt": f"What is the value of the '{field}' metadata field for topic page {topic_filename}?",
            "rule": "Never include the real SHA-256 hash in the prompt to prevent prompt-echo false positives."
        })
    return queries

if __name__ == "__main__":
    print(json.dumps(generate_probe_queries("ceis-support-faq--218dfe1f.html"), indent=2))
