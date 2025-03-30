# CDK Infrastructure

This directory contains the AWS CDK infrastructure code for deploying the application stacks.

## Prerequisites

- Python 3.7 or higher
- AWS CDK CLI
- AWS credentials configured

## Structure

- `app.py` - The main CDK app entry point
- `stacks/` - Infrastructure stack definitions
  - `network_stack.py` - VPC and network resources
  - `database_stack.py` - Aurora and RDS resources  
  - `auth_stack.py` - Cognito authentication resources
  - `monitoring_stack.py` - CloudWatch and monitoring resources
  - `storage_stack.py` - S3 buckets and storage resources
  - `lang_portal/` - Lang Portal stacks
  - `haiku_generator/` - Haiku Generator stacks
  - `vocab_generator/` - Vocab Generator stacks
  - `writing_practice/` - Writing Practice stacks

## Development

### Prerequisites

Setup GitHub connection:

1. Go to the AWS Console
2. Navigate to CodeBuild
3. Go to Settings and then Connections
4. Click on "Create connection"
5. Select "GitHub" as the provider
6. Set the connection name to "free-genai-bootcamp-2025"
7. Click "Connect to GitHub"
8. Click "Install a new app"
9. On GitHub, select the repository and click "Install & Authorize"
10. On AWS, click "Connect"
11. Copy the connection ARN and paste it into the .env file as the environment variable `GITHUB_CONNECTION_ARN`

### Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Synthesize CloudFormation template:
```bash 
cdk synth
```

4. Deploy stacks:
```bash
cdk deploy
```