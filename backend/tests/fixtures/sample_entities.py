import json

def get_sample_domain_data():
    return {
        "entity_type": "domain",
        "value": "example.com",
        "risk_level": "LOW",
        "metadata": {
            "registrar": "GoDaddy",
            "creation_date": "2020-01-01"
        }
    }

def get_sample_ip_data():
    return {
        "entity_type": "ip",
        "value": "1.2.3.4",
        "risk_level": "MEDIUM",
        "metadata": {
            "country": "US",
            "org": "Amazon"
        }
    }
