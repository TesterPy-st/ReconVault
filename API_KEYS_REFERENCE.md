# API Keys Reference

This document lists all the external APIs used by ReconVault and how to configure them.

## Social Media APIs

### Twitter API
- **Purpose**: Collect tweets, user profiles, trends.
- **Env Variable**: `TWITTER_API_KEY`
- **Setup**: Obtain from [Twitter Developer Portal](https://developer.twitter.com/en/docs/twitter-api).

### GitHub API
- **Purpose**: Repository, user, and organization data collection.
- **Env Variable**: `GITHUB_TOKEN`
- **Setup**: Create a Personal Access Token in [GitHub Settings](https://github.com/settings/tokens).

## Threat Intelligence APIs

### Shodan API
- **Purpose**: IP/port scanning, device discovery, and vulnerability data.
- **Env Variable**: `SHODAN_API_KEY`
- **Setup**: Get a key from [Shodan.io](https://www.shodan.io/).

### HaveIBeenPwned API
- **Purpose**: Check for email addresses in data breaches.
- **Env Variable**: `HIBP_API_KEY`
- **Setup**: Purchase an API key from [haveibeenpwned.com](https://haveibeenpwned.com/API/Key).

### VirusTotal API
- **Purpose**: File and URL analysis, reputation checking.
- **Env Variable**: `VIRUSTOTAL_API_KEY`
- **Setup**: Sign up at [VirusTotal](https://www.virustotal.com/).

### AbuseIPDB API
- **Purpose**: Check IP reputation and report abuse.
- **Env Variable**: `ABUSEIPDB_API_KEY`
- **Setup**: Get a key from [AbuseIPDB](https://www.abuseipdb.com/).

## ML/AI APIs

### OpenAI API
- **Purpose**: Entity classification, text analysis, and report generation assistance.
- **Env Variable**: `OPENAI_API_KEY`
- **Setup**: Obtain from [OpenAI Platform](https://platform.openai.com/api-keys).

## Cloud Services

### AWS (Amazon Web Services)
- **Purpose**: Optional S3 storage for report exports.
- **Env Variables**:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`
- **Setup**: Create IAM credentials in the [AWS Console](https://console.aws.amazon.com/).
