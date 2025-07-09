#!/usr/bin/env python3
"""
Distribution Package Creator for Invoice System
==============================================

This script creates a clean, ready-to-distribute package of the invoice system.
Perfect for:
- Creating releases
- Preparing demo versions
- Selling/distributing the software

The packaged version will be completely clean with no user data.
"""

import os
import shutil
import zipfile
import sys
from datetime import datetime

def create_distribution_package():
    """Create a clean distribution package"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"invoice_system_v1.0_{timestamp}"
    package_dir = f"dist/{package_name}"
    
    print(f"📦 Creating distribution package: {package_name}")
    print("=" * 60)
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Remove existing package directory if it exists
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    # Files and directories to include in distribution
    include_items = [
        # Core application files
        'app.py',
        'config.py',
        'requirements.txt',
        'README.md',
        
        # Utility scripts
        'reset_data.py',
        
        # Source code directories
        'models/',
        'routes/',
        'services/',
        'templates/',
        'static/',
    ]
    
    # Files to exclude from directories
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '.env',
        'local_settings.py'
    ]
    
    def should_exclude(path):
        """Check if a file/directory should be excluded"""
        for pattern in exclude_patterns:
            if pattern.replace('*', '') in path:
                return True
        return False
    
    # Copy files to package directory
    print("\n📁 Copying files...")
    
    for item in include_items:
        src_path = item
        dst_path = os.path.join(package_dir, item)
        
        if not os.path.exists(src_path):
            print(f"⚠️  Skipping {item} (not found)")
            continue
        
        if os.path.isfile(src_path):
            # Copy individual file
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"✅ Copied file: {item}")
            
        elif os.path.isdir(src_path):
            # Copy directory, excluding unwanted files
            def ignore_patterns(dir, files):
                return [f for f in files if should_exclude(os.path.join(dir, f))]
            
            shutil.copytree(src_path, dst_path, ignore=ignore_patterns)
            print(f"✅ Copied directory: {item}")
    
    # Create additional distribution files
    print("\n📝 Creating distribution files...")
    
    # Create INSTALL.txt
    install_content = """
INVOICE SYSTEM - INSTALLATION GUIDE
==================================

Thank you for purchasing the Invoice System!

QUICK START:
-----------
1. Make sure Python 3.7+ is installed on your computer
2. Open a terminal/command prompt in this directory
3. Run: pip install -r requirements.txt
4. Run: python app.py
5. Open your browser to: http://localhost:5000

DETAILED SETUP:
--------------
See README.md for complete installation and usage instructions.

FIRST TIME SETUP:
----------------
1. Setup your contractor information (your business details)
2. Add your first client
3. Create your first invoice
4. Mark invoice as paid to generate a receipt

SUPPORT:
-------
For technical support, please check the README.md file
or visit our support documentation.

RESET DATA:
----------
To start with fresh data, run: python reset_data.py

Enjoy your new Invoice System!
"""
    
    with open(os.path.join(package_dir, 'INSTALL.txt'), 'w') as f:
        f.write(install_content.strip())
    print("✅ Created INSTALL.txt")
    
    # Create LICENSE file (if it doesn't exist)
    license_path = os.path.join(package_dir, 'LICENSE')
    if not os.path.exists('LICENSE'):
        license_content = """
MIT License

Copyright (c) 2024 Invoice System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        with open(license_path, 'w') as f:
            f.write(license_content.strip())
        print("✅ Created LICENSE")
    
    # Create VERSION file
    version_content = f"""
Invoice System v1.0
Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python: 3.7+
Framework: Flask 2.3+

Features:
- Professional invoice and receipt generation
- Client management
- Local SQLite database
- Beautiful PDF exports
- Dashboard with statistics
- Tax ID support
- Legal compliance features
"""
    
    with open(os.path.join(package_dir, 'VERSION'), 'w') as f:
        f.write(version_content.strip())
    print("✅ Created VERSION")
    
    # Calculate package size
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
            file_count += 1
    
    print(f"\n📊 Package Statistics:")
    print(f"   Files: {file_count}")
    print(f"   Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # Create ZIP archive
    print(f"\n🗜️  Creating ZIP archive...")
    zip_path = f"dist/{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
    
    zip_size = os.path.getsize(zip_path)
    print(f"✅ Created ZIP: {zip_path} ({zip_size:,} bytes, {zip_size/1024/1024:.1f} MB)")
    
    print(f"\n🎉 Distribution package created successfully!")
    print(f"📁 Directory: {package_dir}")
    print(f"📦 ZIP file: {zip_path}")
    print(f"\n💡 The package is ready for distribution and contains no user data.")
    
    return package_dir, zip_path

def clean_dist_directory():
    """Clean old distribution packages"""
    if os.path.exists("dist"):
        print("🧹 Cleaning old distribution packages...")
        for item in os.listdir("dist"):
            item_path = os.path.join("dist", item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"✅ Removed old package: {item}")
            elif item.endswith('.zip'):
                os.remove(item_path)
                print(f"✅ Removed old ZIP: {item}")

def main():
    """Main function"""
    print("📦 Invoice System - Distribution Packager")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please run this script from the invoice system root directory.")
        return False
    
    print("This will create a clean distribution package with no user data.")
    print("Perfect for:")
    print("  • 🎁 Selling or distributing the software")
    print("  • 🚀 Creating demo versions")
    print("  • 📋 Preparing releases")
    
    choice = input("\n🤔 Do you want to proceed? (yes/no): ").lower().strip()
    
    if choice not in ['yes', 'y']:
        print("❌ Operation cancelled")
        return False
    
    # Clean old packages
    clean_dist_directory()
    
    # Create new package
    try:
        package_dir, zip_path = create_distribution_package()
        
        print(f"\n🎊 SUCCESS!")
        print(f"Your distribution package is ready:")
        print(f"📁 {package_dir}")
        print(f"📦 {zip_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)