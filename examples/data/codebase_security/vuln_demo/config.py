"""Configuration. DO NOT USE: deliberately vulnerable.

Contains test-vector credentials that look real to secret scanners
but are documented as examples in AWS / GitHub / Slack docs.
"""

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
# Fake webhook structure: looks like a Slack URL to detect-secrets but is
# structurally invalid so GitHub's push-protection scanner does not flag it
# as a real secret.
SLACK_WEBHOOK_URL = "https://hooks.example-slack/services/" + "T00000000/B00000000/" + "x" * 24
