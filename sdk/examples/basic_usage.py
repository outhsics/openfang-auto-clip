#!/usr/bin/env python3
"""
Basic Usage Example

Demonstrates basic SDK usage.
"""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openfang_sdk import Client


def main():
    """Run basic usage example"""

    # Initialize client
    print("🔧 Connecting to OpenFang API...")
    client = Client(base_url="http://localhost:8000")

    # Health check
    print("\n📊 Checking API health...")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Version: {health['version']}")

    # Example transcript (if available)
    demo_transcript = Path(__file__).parent.parent.parent / "examples" / "demo" / "sample_level2_transcript.srt"

    if demo_transcript.exists():
        print(f"\n📄 Found demo transcript: {demo_transcript.name}")

        # Upload transcript
        print("\n⬆️  Uploading transcript...")
        upload_info = client.upload_file(str(demo_transcript))
        print(f"   File ID: {upload_info['file_id']}")
        print(f"   Size: {upload_info['size']} bytes")

        # Process
        print("\n🎬 Starting Level 2 processing...")
        job = client.process(
            level=2,
            uploaded_file_id=upload_info['file_id'],
            config={
                "content_type": "auto",
                "default_duration": 60
            }
        )
        print(f"   Job ID: {job['job_id']}")
        print(f"   Status: {job['status']}")

        # Wait for completion
        print("\n⏳ Waiting for job to complete...")
        try:
            result = client.wait_for_job(job['job_id'], timeout=60)
            print(f"   Status: {result['status']}")
            print(f"   Progress: {result['progress']}%")

            if result['status'] == 'completed':
                print(f"\n✅ Processing complete!")
                print(f"   Result: {result['result']}")
            else:
                print(f"\n❌ Processing failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    else:
        print(f"\n⚠️  Demo transcript not found at {demo_transcript}")
        print("   Please provide a transcript file to process")

    # List jobs
    print("\n📋 Recent jobs:")
    jobs = client.list_jobs(limit=5)
    for job in jobs:
        print(f"   {job['id'][:8]}... - {job['status']} ({job['progress']}%)")

    # Close client
    client.close()

    print("\n✅ Example complete!")


if __name__ == "__main__":
    main()
