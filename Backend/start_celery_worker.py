"""
Script untuk memulai Celery worker untuk pembelajaran
"""

import os
import subprocess
import sys


def start_worker():
    """Start Celery worker dengan konfigurasi optimal untuk pembelajaran"""

    print("🚀 Starting Celery Worker for Learning")
    print("=" * 50)

    # Command untuk start worker
    cmd = [
        "celery",
        "-A",
        "app.tasks",
        "worker",
        "-Q",
        "queue_agent_task",
        "--loglevel=info",  # Log level yang informatif
        "--concurrency=1",  # Single worker untuk debugging
        "--pool=solo",  # Pool yang kompatibel dengan Windows
    ]

    print(f"Command: {' '.join(cmd)}")
    print("\n📋 Worker akan:")
    print("- Mendengarkan queue 'celery'")
    print("- Menampilkan log yang detail")
    print("- Menggunakan single worker untuk debugging")
    print("- Kompatibel dengan Windows")
    print("\n⏹️  Tekan Ctrl+C untuk menghentikan worker")
    print("=" * 50)

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n🛑 Worker dihentikan oleh user")
        print("✅ Sampai jumpa lagi!")


if __name__ == "__main__":
    start_worker()
