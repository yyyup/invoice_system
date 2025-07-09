#!/usr/bin/env python3
"""
Database Reset Utility for Invoice System
==========================================

This script provides options to reset or clean the invoice system database.
Use this for:
- Starting fresh with a clean database
- Preparing the system for distribution
- Removing test data

CAUTION: This will permanently delete your data!
Make sure to backup important invoices and receipts before running.
"""

import os
import shutil
import sys
from datetime import datetime

def confirm_action(message):
    """Ask user for confirmation before destructive actions"""
    while True:
        response = input(f"{message} (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'")

def backup_data():
    """Create a backup of current data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup database
        if os.path.exists("data"):
            shutil.copytree("data", os.path.join(backup_dir, "data"))
            print(f"✅ Database backed up to {backup_dir}/data/")
        
        # Backup PDFs
        if os.path.exists("pdfs"):
            shutil.copytree("pdfs", os.path.join(backup_dir, "pdfs"))
            print(f"✅ PDFs backed up to {backup_dir}/pdfs/")
        
        return backup_dir
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def remove_database():
    """Remove the database file"""
    db_path = "data/invoices.db"
    data_dir = "data"
    
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Database file removed")
        
        if os.path.exists(data_dir) and not os.listdir(data_dir):
            os.rmdir(data_dir)
            print("✅ Empty data directory removed")
        
        return True
    except Exception as e:
        print(f"❌ Failed to remove database: {e}")
        return False

def remove_pdfs():
    """Remove generated PDF files"""
    pdfs_dir = "pdfs"
    
    try:
        if os.path.exists(pdfs_dir):
            shutil.rmtree(pdfs_dir)
            print("✅ PDF directory removed")
        return True
    except Exception as e:
        print(f"❌ Failed to remove PDFs: {e}")
        return False

def clean_pycache():
    """Remove Python cache files"""
    try:
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path)
                    print(f"✅ Removed {pycache_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to clean cache: {e}")
        return False

def distribution_clean():
    """Clean everything for distribution package"""
    print("🧹 DISTRIBUTION CLEAN")
    print("=" * 50)
    print("This will remove ALL user data and prepare for distribution.")
    print("⚠️  This includes:")
    print("   - Database with all invoices, clients, receipts")
    print("   - Generated PDF files")
    print("   - Python cache files")
    print("   - Any test data")
    
    if not confirm_action("\n🚨 Are you ABSOLUTELY SURE you want to continue?"):
        print("❌ Operation cancelled")
        return False
    
    print("\n🧹 Cleaning for distribution...")
    
    # Remove all user data
    success = True
    success &= remove_database()
    success &= remove_pdfs()
    success &= clean_pycache()
    
    if success:
        print("\n✅ Distribution clean completed successfully!")
        print("📦 Ready for packaging or distribution")
        print("\n💡 The system will create fresh directories when first run")
        return True
    else:
        print("\n❌ Some cleaning operations failed")
        return False

def reset_with_backup():
    """Reset data but create backup first"""
    print("🔄 RESET WITH BACKUP")
    print("=" * 50)
    print("This will:")
    print("   1. Create a backup of your current data")
    print("   2. Reset the database to start fresh")
    print("   3. Keep your PDFs backed up")
    
    if not confirm_action("\n🤔 Do you want to proceed?"):
        print("❌ Operation cancelled")
        return False
    
    print("\n📦 Creating backup...")
    backup_dir = backup_data()
    
    if not backup_dir:
        print("❌ Backup failed - aborting reset")
        return False
    
    print(f"✅ Backup created at: {backup_dir}")
    
    if confirm_action("\n🗑️  Now reset the database?"):
        if remove_database():
            print("\n✅ Database reset completed!")
            print(f"📁 Your old data is backed up in: {backup_dir}")
            print("🚀 You can now start with a fresh database")
            return True
        else:
            print("\n❌ Database reset failed")
            return False
    else:
        print("❌ Reset cancelled - backup is still available")
        return False

def quick_reset():
    """Quick reset without backup (for development)"""
    print("⚡ QUICK RESET")
    print("=" * 50)
    print("This will immediately delete all data without backup.")
    print("⚠️  Use only for development/testing!")
    
    if not confirm_action("\n🚨 Are you sure? This cannot be undone!"):
        print("❌ Operation cancelled")
        return False
    
    print("\n🗑️  Removing all data...")
    
    success = True
    success &= remove_database()
    success &= remove_pdfs()
    
    if success:
        print("\n✅ Quick reset completed!")
        print("🚀 Ready for fresh start")
        return True
    else:
        print("\n❌ Reset failed")
        return False

def show_status():
    """Show current status of data files"""
    print("📊 CURRENT STATUS")
    print("=" * 50)
    
    # Check database
    db_path = "data/invoices.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"💾 Database: EXISTS ({size:,} bytes)")
    else:
        print("💾 Database: NOT FOUND")
    
    # Check PDFs
    pdfs_dir = "pdfs"
    if os.path.exists(pdfs_dir):
        total_files = 0
        total_size = 0
        for root, dirs, files in os.walk(pdfs_dir):
            total_files += len(files)
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        print(f"📄 PDFs: {total_files} files ({total_size:,} bytes)")
    else:
        print("📄 PDFs: NOT FOUND")
    
    # Check cache
    cache_count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in root:
            cache_count += len(files)
    if cache_count > 0:
        print(f"🗂️  Cache: {cache_count} files")
    else:
        print("🗂️  Cache: CLEAN")

def main():
    """Main menu for reset operations"""
    print("🧹 Invoice System - Data Reset Utility")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. 📊 Show current status")
        print("2. 🔄 Reset with backup (recommended)")
        print("3. ⚡ Quick reset (no backup)")
        print("4. 📦 Distribution clean (remove everything)")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            show_status()
        elif choice == '2':
            reset_with_backup()
        elif choice == '3':
            quick_reset()
        elif choice == '4':
            distribution_clean()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)