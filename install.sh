#!/bin/bash

# Arch Update GUI Installer
# This script installs all dependencies and sets up the application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Arch-based system
check_system() {
    print_info "Checking system compatibility..."
    if [ ! -f /etc/arch-release ] && [ ! -f /etc/manjaro-release ]; then
        print_error "This installer is designed for Arch Linux and Arch-based distributions."
        exit 1
    fi
    print_success "System check passed"
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # List of required packages
    PACKAGES=(
        "python"
        "python-pip"
        "python-virtualenv"
        "pacman-contrib"
        "zenity"
        "libnotify"
    )
    
    # Check for yay
    if ! command -v yay &> /dev/null; then
        print_warning "yay not found. It's recommended for AUR support."
        read -p "Install yay? (y/n): " install_yay
        if [[ $install_yay == "y" ]]; then
            print_info "Installing yay..."
            sudo pacman -S --needed --noconfirm git base-devel
            cd /tmp
            git clone https://aur.archlinux.org/yay.git
            cd yay
            makepkg -si --noconfirm
            cd -
            print_success "yay installed"
        fi
    fi
    
    # Install packages
    print_info "Installing packages: ${PACKAGES[*]}"
    sudo pacman -S --needed --noconfirm "${PACKAGES[@]}"
    
    print_success "System dependencies installed"
}

# Setup Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install PySide6
    deactivate
    
    print_success "Python environment ready"
}

# Make script executable
setup_permissions() {
    print_info "Setting up permissions..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    chmod +x "$SCRIPT_DIR/update_gui.py"
    
    print_success "Permissions set"
}

# Create desktop launcher
create_launcher() {
    print_info "Creating desktop launcher..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    DESKTOP_FILE="$HOME/.local/share/applications/arch-update-gui.desktop"
    
    # Create .local/share/applications if it doesn't exist
    mkdir -p "$HOME/.local/share/applications"
    
    # Create desktop entry
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Arch Update GUI
Comment=Graphical system update manager for Arch Linux
Exec=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/update_gui.py
Icon=system-software-update
Terminal=false
Categories=System;Settings;PackageManager;
Keywords=update;upgrade;pacman;aur;yay;
EOF
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications"
    fi
    
    print_success "Desktop launcher created at $DESKTOP_FILE"
}

# Create uninstall script
create_uninstaller() {
    print_info "Creating uninstall script..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    cat > "$SCRIPT_DIR/uninstall.sh" << 'EOF'
#!/bin/bash

# Arch Update GUI Uninstaller

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$HOME/.local/share/applications/arch-update-gui.desktop"

echo "Uninstalling Arch Update GUI..."

# Remove desktop launcher
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "Removed desktop launcher"
fi

# Remove virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    rm -rf "$SCRIPT_DIR/venv"
    echo "Removed virtual environment"
fi

# Remove config
CONFIG_DIR="$HOME/.config/MyOrg"
if [ -d "$CONFIG_DIR" ]; then
    read -p "Remove configuration files? (y/n): " remove_config
    if [[ $remove_config == "y" ]]; then
        rm -rf "$CONFIG_DIR"
        echo "Removed configuration"
    fi
fi

echo "Uninstall complete!"
echo "Note: System packages (zenity, pacman-contrib, etc.) were not removed."
EOF
    
    chmod +x "$SCRIPT_DIR/uninstall.sh"
    print_success "Uninstaller created at $SCRIPT_DIR/uninstall.sh"
}

# Main installation process
main() {
    echo ""
    echo "======================================"
    echo "  Arch Update GUI Installer"
    echo "======================================"
    echo ""
    
    check_system
    echo ""
    
    install_dependencies
    echo ""
    
    setup_venv
    echo ""
    
    setup_permissions
    echo ""
    
    create_launcher
    echo ""
    
    create_uninstaller
    echo ""
    
    print_success "Installation complete!"
    echo ""
    echo "You can now:"
    echo "  1. Launch from your application menu: 'Arch Update GUI'"
    echo "  2. Run from terminal: ./update_gui.py"
    echo "  3. Run with: ./venv/bin/python update_gui.py"
    echo ""
    echo "To uninstall, run: ./uninstall.sh"
    echo ""
}

# Run main installation
main
