"""
Deploy Weather Assistant Agent to Vertex AI Agent Engine.

This script packages and deploys the agent to Agent Engine using the ADK CLI.

Prerequisites:
- Google Cloud project with billing enabled
- Vertex AI API enabled
- ADK CLI installed: pip install google-adk
- Authenticated with gcloud: gcloud auth login

Usage:
    python deploy_to_agent_engine.py --project-id YOUR_PROJECT_ID --region us-east4
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def deploy_agent(project_id: str, region: str, agent_dir: str = None):
    """
    Deploy agent to Vertex AI Agent Engine.

    Args:
        project_id: Google Cloud project ID
        region: Deployment region (e.g., us-east4, europe-west1)
        agent_dir: Directory containing agent files (default: WeatherAssistant)
    """
    if agent_dir is None:
        agent_dir = Path(__file__).parent / "WeatherAssistant"

    agent_dir = Path(agent_dir)
    config_file = agent_dir / ".agent_engine_config.json"

    if not agent_dir.exists():
        raise ValueError(f"Agent directory not found: {agent_dir}")

    if not config_file.exists():
        raise ValueError(f"Config file not found: {config_file}")

    print("=" * 60)
    print("Deploying Weather Assistant to Agent Engine")
    print("=" * 60)
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print(f"Agent Directory: {agent_dir}")
    print("=" * 60)

    # Build the adk deploy command
    cmd = [
        "adk",
        "deploy",
        "agent_engine",
        "--project",
        project_id,
        "--region",
        region,
        str(agent_dir),
        "--agent_engine_config_file",
        str(config_file),
    ]

    print(f"\nRunning: {' '.join(cmd)}\n")

    # Run the deployment command
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("\n✅ Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Wait 2-5 minutes for the agent to be ready")
        print("2. Use test_deployed_agent.py to test your deployed agent")
        print(
            f"3. View in console: https://console.cloud.google.com/vertex-ai/agents/agent-engines?project={project_id}"
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ ADK CLI not found. Please install it:")
        print("   pip install google-adk")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Deploy agent to Vertex AI Agent Engine")
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.getenv("GOOGLE_CLOUD_PROJECT"),
        help="Google Cloud project ID (default: from GOOGLE_CLOUD_PROJECT env var)",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=os.getenv("AGENT_ENGINE_REGION", "us-east4"),
        help="Deployment region (default: us-east4)",
    )
    parser.add_argument(
        "--agent-dir",
        type=str,
        default=None,
        help="Agent directory path (default: WeatherAssistant)",
    )

    args = parser.parse_args()

    if not args.project_id:
        print("❌ Error: --project-id is required or set GOOGLE_CLOUD_PROJECT env var")
        sys.exit(1)

    success = deploy_agent(args.project_id, args.region, args.agent_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

