"""
Cleanup script to delete deployed agents from Vertex AI Agent Engine.

⚠️ IMPORTANT: Always delete resources when done testing to avoid costs!

Usage:
    python cleanup_agent.py --project-id YOUR_PROJECT_ID --region us-east4
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

import vertexai
from vertexai import agent_engines

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def cleanup_agents(project_id: str, region: str, force: bool = True):
    """
    Delete all deployed agents in the specified region.

    Args:
        project_id: Google Cloud project ID
        region: Deployment region
        force: Force deletion even if agent is running
    """
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=region)

    print("=" * 60)
    print("Cleaning Up Deployed Agents")
    print("=" * 60)
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print("=" * 60)

    # List all agents
    agents_list = list(agent_engines.list())
    
    if not agents_list:
        print("\n✅ No agents found. Nothing to clean up.")
        return

    print(f"\nFound {len(agents_list)} agent(s):")
    for i, agent in enumerate(agents_list, 1):
        print(f"  {i}. {agent.resource_name}")

    # Delete each agent
    print(f"\nDeleting {len(agents_list)} agent(s)...")
    for agent in agents_list:
        try:
            print(f"\nDeleting: {agent.resource_name}")
            agent_engines.delete(resource_name=agent.resource_name, force=force)
            print(f"✅ Successfully deleted: {agent.resource_name}")
        except Exception as e:
            print(f"❌ Failed to delete {agent.resource_name}: {e}")

    print("\n✅ Cleanup completed!")
    print("\nNote: Deletion typically takes 1-2 minutes.")
    print(
        f"Verify in console: https://console.cloud.google.com/vertex-ai/agents/agent-engines?project={project_id}"
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Cleanup deployed agents from Vertex AI Agent Engine"
    )
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
        "--no-force",
        action="store_true",
        help="Don't force deletion (default: force=True)",
    )

    args = parser.parse_args()

    if not args.project_id:
        print("❌ Error: --project-id is required or set GOOGLE_CLOUD_PROJECT env var")
        sys.exit(1)

    cleanup_agents(args.project_id, args.region, force=not args.no_force)


if __name__ == "__main__":
    main()

