#!/usr/bin/python3

# Adam Stout
# 3/10/2024
# NSSA 244

import subprocess
import sys
import os

def list_vms():
    print("Available VMs:")
    try:
        output = subprocess.check_output(["VBoxManage", "list", "vms"], stderr=subprocess.DEVNULL)
        vms = output.decode("utf-8").strip()
        if vms:
            print(vms)
        else:
            print("No VMs found.")
    except subprocess.CalledProcessError:
        print("Failed to list VMs.")

def start_vm(vm_name):
    try:
        subprocess.run(["VBoxManage", "startvm", vm_name], check=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Failed to start VM '{vm_name}'. VM does not exist or failed to start.")

def stop_vm(vm_name):
    try:
        subprocess.run(["VBoxManage", "controlvm", vm_name, "poweroff"], check=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Failed to stop VM '{vm_name}'. VM is not started.")

def create_vm():
    try:
        vm_name = input("Enter the name for the new VM: ")
        vm_os = input("Enter the OS type (e.g., 'Linux', 'Windows'): ")
        memory_size = input("Enter the memory size in MB: ")
        disk_size = input("Enter the disk size in MB: ")

        # Validate memory size and disk size
        try:
            memory_size = int(memory_size)
            if memory_size <= 0:
                print("Error: Memory size must be a positive integer.")
                return
            elif memory_size > 128000:  # Limit memory to 128GB
                print("Error: Memory size must not exceed 128GB.")
                return
        except ValueError:
            print("Error: Memory size must be a valid integer.")
            return

        try:
            disk_size = int(disk_size)
            if disk_size <= 0:
                print("Error: Disk size must be a positive integer.")
                return
            elif disk_size > 2000000:  # Limit disk size to 2TB
                print("Error: Disk size must not exceed 2TB.")
                return
        except ValueError:
            print("Error: Disk size must be a valid integer.")
            return

        # Create directory for the VM
        vm_directory = os.path.join(os.getcwd(), vm_name)
        os.makedirs(vm_directory, exist_ok=True)

        # Create the VM
        result = subprocess.run(["VBoxManage", "createvm", "--name", vm_name, "--ostype", vm_os, "--register"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"VM '{vm_name}' created successfully.")
        elif "already exists" in result.stderr:
            print(f"Error: Failed to create VM '{vm_name}' - VM with the same name already exists.")
            return
        else:
            print(f"Error: Command returned non-zero exit status {result.returncode}")
            return

        # Set memory size
        try:
            subprocess.run(["VBoxManage", "modifyvm", vm_name, "--memory", str(memory_size)], check=True, stderr=subprocess.DEVNULL)
            print(f"Memory size set successfully for VM '{vm_name}'.")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to set memory size for VM '{vm_name}'.")

        # Add SATA controller
        try:
            subprocess.run(["VBoxManage", "storagectl", vm_name, "--name", "SATA", "--add", "sata"], check=True, stderr=subprocess.DEVNULL)
            print(f"SATA controller added to VM '{vm_name}'.")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to add SATA controller to VM '{vm_name}'.")

        # Create virtual disk
        try:
            subprocess.run(["VBoxManage", "createhd", "--filename", f"{vm_name}/{vm_name}.vdi", "--size", str(disk_size)], check=True, stderr=subprocess.DEVNULL)
            print(f"Virtual disk created successfully for VM '{vm_name}'.")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to create virtual disk for VM '{vm_name}'.")

        # Attach virtual disk
        try:
            subprocess.run(["VBoxManage", "storageattach", vm_name, "--storagectl", "SATA", "--port", "0", "--device", "0", "--type", "hdd", "--medium", f"{vm_name}/{vm_name}.vdi"], check=True, stderr=subprocess.DEVNULL)
            print(f"Virtual disk attached successfully to VM '{vm_name}'.")
        except subprocess.CalledProcessError:
            print(f"Error: Failed to attach virtual disk for VM '{vm_name}'.")

    except FileNotFoundError:
        print("Error: VBoxManage command not found. Make sure VirtualBox is installed and added to system PATH.")
    except KeyboardInterrupt:
        print("Operation interrupted.")

def delete_vm(vm_name):
    confirmation = input(f"Are you sure you want to delete VM '{vm_name}'? (yes/no): ").lower()
    if confirmation == 'yes' or confirmation == 'y':
        try:
            subprocess.run(["VBoxManage", "unregistervm", vm_name, "--delete"], check=True, stderr=subprocess.DEVNULL)
            print('\nVM deleted successfully!')
        except subprocess.CalledProcessError:
            print(f"Failed to delete VM '{vm_name}'. VM does not exist.")
    else:
        print("Deletion canceled.")

def vm_settings(vm_name):
    try:
        subprocess.run(["VBoxManage", "showvminfo", vm_name], check=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Failed to retrieve settings for VM '{vm_name}'. VM does not exist.")

def manage_snapshots(vm_name):
    try:
        vms = subprocess.check_output(["VBoxManage", "list", "vms"], stderr=subprocess.DEVNULL)
        if vm_name not in vms.decode("utf-8"):
            print(f"Error: VM '{vm_name}' does not exist.")
            return

        while True:
            print("\nManage Snapshots:")
            print("1. Take a snapshot")
            print("2. List snapshots")
            print("3. Restore a snapshot")
            print("4. Delete a snapshot")
            print("5. Go back")

            choice = input("Enter your choice: ")

            if choice == '1':
                snapshot_name = input("Enter the name for the snapshot: ")
                try:
                    subprocess.run(["VBoxManage", "snapshot", vm_name, "take", snapshot_name], check=True, stderr=subprocess.DEVNULL)
                    print(f"Snapshot '{snapshot_name}' taken successfully.")
                except subprocess.CalledProcessError:
                    print("Failed to take snapshot.")
            elif choice == '2':
                try:
                    output = subprocess.check_output(["VBoxManage", "snapshot", vm_name, "list"], stderr=subprocess.DEVNULL)
                    print(output.decode("utf-8"))
                except subprocess.CalledProcessError:
                    print("No snapshots found.")
            elif choice == '3':
                snapshot_name = input("Enter the name of the snapshot to restore: ")
                try:
                    subprocess.run(["VBoxManage", "snapshot", vm_name, "restore", snapshot_name], check=True, stderr=subprocess.DEVNULL)
                    print(f"Snapshot '{snapshot_name}' restored successfully.")
                except subprocess.CalledProcessError:
                    print(f"Failed to restore snapshot '{snapshot_name}'. Snapshot not found.")
            elif choice == '4':
                snapshot_name = input("Enter the name of the snapshot to delete: ")
                try:
                    subprocess.run(["VBoxManage", "snapshot", vm_name, "delete", snapshot_name], check=True, stderr=subprocess.DEVNULL)
                    print(f"Snapshot '{snapshot_name}' deleted successfully.")
                except subprocess.CalledProcessError:
                    print(f"Failed to delete snapshot '{snapshot_name}'.")
            elif choice == '5':
                break
            else:
                print("Invalid choice, please try again.")
    except subprocess.CalledProcessError:
        print("Error: Failed to manage snapshots.")


def main_menu():
    while True:
        print("\nVirtualBox Manager")
        print("1. List VMs")
        print("2. Start a VM")
        print("3. Stop a VM")
        print("4. Create a VM")
        print("5. Delete a VM")
        print("6. VM Settings")
        print("7. Manage VM Snapshots")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            list_vms()
        elif choice == '2':
            vm_name = input("Enter the name of the VM to start: ")
            start_vm(vm_name)
        elif choice == '3':
            vm_name = input("Enter the name of the VM to stop: ")
            stop_vm(vm_name)
        elif choice == '4':
            create_vm()
        elif choice == '5':
            vm_name = input("Enter the name of the VM to delete: ")
            delete_vm(vm_name)
        elif choice == '6':
            vm_name = input("Enter the name of the VM to view settings: ")
            vm_settings(vm_name)
        elif choice == '7':
            vm_name = input("Enter the name of the VM to manage snapshots: ")
            manage_snapshots(vm_name)
        elif choice == '8':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
