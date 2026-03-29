#!/usr/bin/env python3
"""
Batch Processing Example

Demonstrates processing multiple transcripts.
"""

import sys
import time
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openfang_sdk import Client, ProcessingError


def main():
    """Run batch processing example"""

    # Initialize client
    print("🚀 Batch Processing Example")
    print("=" * 50)

    client = Client(base_url="http://localhost:8000")

    # Demo transcripts
    demo_dir = Path(__file__).parent.parent.parent / "examples" / "demo"
    transcripts = list(demo_dir.glob("*.srt"))

    if not transcripts:
        print("❌ No transcript files found in demo directory")
        return

    print(f"\n📄 Found {len(transcripts)} transcript(s)")

    # Start all jobs
    print("\n⬆️  Starting jobs...")
    jobs = []

    for i, transcript in enumerate(transcripts, 1):
        try:
            print(f"\n[{i}/{len(transcripts)}] Processing {transcript.name}...")

            # Upload
            upload_info = client.upload_file(str(transcript))

            # Start processing
            job = client.process(
                level=2,
                uploaded_file_id=upload_info['file_id'],
                config={"content_type": "auto"}
            )

            jobs.append({
                'name': transcript.name,
                'job_id': job['job_id']
            })

            print(f"   ✅ Job started: {job['job_id'][:8]}...")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # Monitor progress
    print(f"\n⏳ Monitoring {len(jobs)} job(s)...")
    print("-" * 50)

    completed = 0
    start_time = time.time()

    while completed < len(jobs):
        for job_info in jobs:
            if 'status' in job_info:
                continue  # Already completed/failed

            try:
                job = client.get_job(job_info['job_id'])
                status = job['status']
                progress = job['progress']

                print(f"{job_info['name'][:30]:30} {status:12} {progress:6.1f}%")

                if status in ['completed', 'failed']:
                    job_info['status'] = status
                    job_info['result'] = job
                    completed += 1

            except Exception as e:
                print(f"{job_info['name'][:30]:30} Error: {e}")

        if completed < len(jobs):
            time.sleep(2)
            print()  # Blank line between updates

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    print(f"Total jobs: {len(jobs)}")
    print(f"Completed: {sum(1 for j in jobs if j.get('status') == 'completed')}")
    print(f"Failed: {sum(1 for j in jobs if j.get('status') == 'failed')}")
    print(f"Elapsed time: {elapsed:.1f} seconds")
    print(f"Average time: {elapsed/len(jobs):.1f} seconds/job")

    # Show results
    print("\n📁 Results:")
    for job_info in jobs:
        status = job_info.get('status', 'unknown')
        emoji = "✅" if status == "completed" else "❌"
        print(f"   {emoji} {job_info['name']}: {status}")

        if status == 'completed' and 'result' in job_info:
            result = job_info['result']
            if result.get('result'):
                print(f"      Output: {result['result'].get('output_path', 'N/A')}")

    client.close()

    print("\n✅ Batch processing complete!")


if __name__ == "__main__":
    main()
