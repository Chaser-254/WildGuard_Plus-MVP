#!/usr/bin/env python
"""
YOLOv8 Setup Script for WildGuard

This script helps install YOLOv8 and download the pre-trained model.
Supports both CPU and GPU inference.

Usage:
    python scripts/setup_yolov8.py              # Install with CPU support
    python scripts/setup_yolov8.py --gpu        # Install with GPU (CUDA) support
    python scripts/setup_yolov8.py --download   # Download model weights only
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / 'ml' / 'models'


def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def install_yolov8_cpu():
    """Install YOLOv8 with CPU support"""
    print("Installing YOLOv8 with CPU support...")
    
    cmd = [sys.executable, '-m', 'pip', 'install', 'ultralytics', 'opencv-python']
    return run_command(cmd, "YOLOv8 CPU installation")


def install_yolov8_gpu():
    """Install YOLOv8 with GPU (CUDA) support"""
    print("Installing YOLOv8 with GPU support...")
    
    # Install PyTorch with CUDA first
    print("\n📊 Installing PyTorch with CUDA support...")
    torch_cmd = [
        sys.executable, '-m', 'pip', 'install',
        'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu118'
    ]
    
    if not run_command(torch_cmd, "PyTorch CUDA installation"):
        print("⚠️  PyTorch CUDA installation failed. You may need to install CUDA toolkit manually.")
        print("    See: https://pytorch.org/get-started/locally/")
        return False
    
    # Install ultralytics
    cmd = [sys.executable, '-m', 'pip', 'install', 'ultralytics', 'opencv-python']
    return run_command(cmd, "YOLOv8 installation")


def download_model():
    """Download YOLOv8 pre-trained weights"""
    print("\n📥 Downloading YOLOv8 model weights...")
    
    # Create model directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Import ultralytics and download model
        from ultralytics import YOLO
        
        print("Downloading yolov8m (medium model, ~52MB)...")
        model = YOLO('yolov8m.pt')  # This will auto-download
        print(f"✅ Model downloaded successfully!")
        
        # Show model info
        print("\n📋 Model Information:")
        print(f"Model: {model.model_name}")
        print(f"Device: {model.device}")
        
        return True
    
    except ImportError:
        print("❌ ultralytics not installed. Please install it first with --gpu or without --gpu")
        return False
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False


def verify_installation():
    """Verify YOLOv8 is properly installed"""
    print("\n🔍 Verifying YOLOv8 installation...")
    
    try:
        from ultralytics import YOLO
        import torch
        import cv2
        
        print("✅ ultralytics installed")
        print(f"✅ PyTorch installed (version {torch.__version__})")
        print(f"✅ OpenCV installed (version {cv2.__version__})")
        
        # Check GPU availability
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_count = torch.cuda.device_count()
            print(f"✅ GPU support: {gpu_count} GPU(s) detected")
            print(f"   Device: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  GPU not available - will use CPU for inference")
        
        print("\n✅ All dependencies verified successfully!")
        return True
    
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Setup YOLOv8 for WildGuard detection system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup_yolov8.py              # Install CPU version
  python scripts/setup_yolov8.py --gpu        # Install GPU (CUDA) version
  python scripts/setup_yolov8.py --download   # Download model only
  python scripts/setup_yolov8.py --verify     # Verify installation
        """
    )
    
    parser.add_argument('--gpu', action='store_true', help='Install with GPU (CUDA) support')
    parser.add_argument('--download', action='store_true', help='Download model weights only')
    parser.add_argument('--verify', action='store_true', help='Verify installation')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🦁 WildGuard YOLOv8 Setup")
    print("="*60)
    
    # If no args, install CPU version
    if not (args.gpu or args.download or args.verify):
        success = install_yolov8_cpu()
    elif args.gpu:
        success = install_yolov8_gpu()
    elif args.download:
        success = download_model()
    elif args.verify:
        success = verify_installation()
    else:
        success = True
    
    # Always verify at the end
    if success:
        print("\n" + "="*60)
        if not args.verify:
            verify_installation()
    
    print("\n" + "="*60)
    if success:
        print("✅ Setup complete! You can now use YOLOv8 detection.")
        print("\nTo enable real detection, update your code:")
        print("  detection_service.detector.switch_mode(use_mock=False)")
        print("  # OR initialize with: get_detection_service(use_mock=False)")
    else:
        print("❌ Setup failed. Please check the errors above.")
    
    print("="*60)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
