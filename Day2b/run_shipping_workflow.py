"""
Standalone script to run the shipping workflow with Long-Running Operations.

This demonstrates the approval workflow:
- Small orders (≤5 containers): Auto-approved
- Large orders (>5 containers): Pauses for approval, then resumes

Usage:
    python run_shipping_workflow.py
"""

import asyncio
from shipping_agent.agent import run_shipping_workflow


async def main():
    """Run demo workflows."""
    print("=" * 60)
    print("Shipping Agent - Long-Running Operations Demo")
    print("=" * 60)
    
    # Demo 1: Small order - auto-approved
    print("\n📦 Demo 1: Small Order (Auto-Approved)")
    await run_shipping_workflow("Ship 3 containers to Singapore")
    
    # Demo 2: Large order - approved
    print("\n📦 Demo 2: Large Order (Approved)")
    await run_shipping_workflow("Ship 10 containers to Rotterdam", auto_approve=True)
    
    # Demo 3: Large order - rejected
    print("\n📦 Demo 3: Large Order (Rejected)")
    await run_shipping_workflow("Ship 8 containers to Los Angeles", auto_approve=False)
    
    print("\n✅ All demos completed!")


if __name__ == "__main__":
    asyncio.run(main())

