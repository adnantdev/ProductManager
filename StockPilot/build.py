# build.py - Fixed Complete Publishing Script
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import json

class PublishManager:
    def __init__(self):
        self.app_name = "StockPilot"
        self.version = "1.0.0"
        self.company = "Your Company"
        self.output_dir = "dist"
        self.icon_path = "src/resources/icons/app.ico"
        
    def check_pyinstaller(self):
        """Check if PyInstaller is installed"""
        try:
            import PyInstaller
            return True
        except ImportError:
            print("❌ PyInstaller not found!")
            print("📦 Installing PyInstaller...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
                print("✅ PyInstaller installed successfully!")
                return True
            except Exception as e:
                print(f"❌ Failed to install PyInstaller: {e}")
                return False
    
    def clean(self):
        """Clean build directories"""
        print("🧹 Cleaning build directories...")
        dirs_to_clean = ['build', 'dist', '__pycache__', '*.spec']
        for pattern in dirs_to_clean:
            if '*' in pattern:
                import glob
                for f in glob.glob(pattern):
                    if os.path.isfile(f):
                        os.remove(f)
                    elif os.path.isdir(f):
                        shutil.rmtree(f)
            else:
                if os.path.exists(pattern):
                    if os.path.isdir(pattern):
                        shutil.rmtree(pattern)
                    else:
                        os.remove(pattern)
        print("✅ Clean complete!")
    
    def create_version_file(self):
        """Create version info file for Windows"""
        version_parts = self.version.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
            
        version_txt = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    prodvers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'{self.company}'),
           StringStruct(u'FileDescription', u'{self.app_name}'),
           StringStruct(u'FileVersion', u'{self.version}'),
           StringStruct(u'InternalName', u'{self.app_name}'),
           StringStruct(u'LegalCopyright', u'© {self.company}. All rights reserved.'),
           StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
           StringStruct(u'ProductName', u'{self.app_name}'),
           StringStruct(u'ProductVersion', u'{self.version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [0x0409, 0x04B0])])
  ]
)
"""
        with open('version.txt', 'w') as f:
            f.write(version_txt)
    
    def create_default_icon(self):
        """Create a default icon if none exists"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            print("🎨 Creating default icon...")
            
            # Create a 256x256 icon
            size = 256
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a blue gradient background
            draw.ellipse([10, 10, size-10, size-10], fill='#0078d4')
            
            # Draw a box icon
            box_size = size * 0.6
            x1 = (size - box_size) / 2
            y1 = (size - box_size) / 2
            x2 = x1 + box_size
            y2 = y1 + box_size
            
            draw.rectangle([x1, y1, x2, y2], outline='white', width=8)
            
            # Draw lines inside the box
            draw.line([x1 + 20, y1 + 40, x2 - 20, y1 + 40], fill='white', width=4)
            draw.line([x1 + 20, y1 + 70, x2 - 20, y1 + 70], fill='white', width=4)
            draw.line([x1 + 20, y1 + 100, x2 - 20, y1 + 100], fill='white', width=4)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(self.icon_path), exist_ok=True)
            
            # Save as ICO
            img.save(self.icon_path, format='ICO', sizes=[(256, 256)])
            print(f"✅ Default icon created at {self.icon_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not create default icon: {e}")
            return False
    
    def build_exe(self):
        """Build Windows executable with your logo"""
        print("🏗️ Building Windows executable...")
        
        # Check PyInstaller
        if not self.check_pyinstaller():
            print("❌ PyInstaller is required. Please install it manually:")
            print("   pip install pyinstaller")
            return False
        
        # Check if icon exists
        if not os.path.exists(self.icon_path):
            print(f"⚠️ Icon not found at {self.icon_path}")
            print("Creating default icon...")
            if not self.create_default_icon():
                print("❌ Could not create icon. Please add your own icon.")
                return False
        
        # Check if main.py exists
        if not os.path.exists("src/main.py"):
            print("❌ src/main.py not found!")
            print("   Please make sure your main.py is in the src folder.")
            return False
        
        # Create version file
        self.create_version_file()
        
        # Build PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            '--onefile',
            '--windowed',
            f'--name={self.app_name}',
            f'--version-file=version.txt',
            f'--icon={self.icon_path}',
            '--add-data=src/resources;resources',
            '--hidden-import=PyQt5',
            '--hidden-import=PyQt5.QtChart',
            '--hidden-import=pandas',
            '--hidden-import=openpyxl',
            '--uac-admin',
            '--clean',
            '--noconfirm',
            'src/main.py'
        ]
        
        print("\n📦 Running PyInstaller...")
        print(f"   Command: {' '.join(cmd[:5])} ...")
        print("   This may take a few minutes...\n")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Build failed!")
                print("\nError details:")
                print(result.stderr)
                return False
            
            print("✅ Build successful!")
            
            # Copy icon to dist folder
            if os.path.exists(self.icon_path):
                shutil.copy(self.icon_path, f"dist/{self.app_name}.ico")
            
            # Check if executable was created
            exe_path = f"dist/{self.app_name}.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"\n📁 Executable created: {exe_path}")
                print(f"   Size: {size_mb:.2f} MB")
                return True
            else:
                print("❌ Executable not found after build!")
                return False
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def create_installer(self):
        """Create professional installer using Inno Setup"""
        if platform.system() != 'Windows':
            print("⚠️ Installer creation only available on Windows")
            return False
        
        print("\n📦 Creating professional installer...")
        
        # Check if executable exists
        if not os.path.exists(f"dist/{self.app_name}.exe"):
            print("❌ Executable not found. Please build first.")
            return False
        
        # Check if Inno Setup is installed
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
        ]
        
        inno_found = False
        inno_exe = None
        
        for path in inno_paths:
            if os.path.exists(path):
                inno_found = True
                inno_exe = path
                break
        
        if not inno_found:
            print("\n⚠️ Inno Setup not found!")
            print("   Please install Inno Setup from: https://jrsoftware.org/isinfo.php")
            print("\n   Or download the portable version and run:")
            print("   python build.py --portable-only")
            return False
        
        # Inno Setup script
        iss_script = f"""
[Setup]
AppId={{{self.app_name.replace(' ', '')}}}
AppName={self.app_name}
AppVersion={self.version}
AppPublisher={self.company}
AppPublisherURL=https://yourcompany.com
AppSupportURL=https://yourcompany.com/support
AppUpdatesURL=https://yourcompany.com/updates
DefaultDirName={{pf}}\\{self.app_name}
DefaultGroupName={self.app_name}
AllowNoIcons=yes
OutputDir={self.output_dir}
OutputBaseFilename={self.app_name}_Setup_v{self.version}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=dist\\{self.app_name}.ico
UninstallDisplayIcon={{app}}\\app.ico
PrivilegesRequired=admin
DisableProgramGroupPage=no
DisableReadyPage=no
LicenseFile=LICENSE
AppCopyright=Copyright (c) 2024 {self.company}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\\{self.app_name}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "src\\resources\\*"; DestDir: "{{app}}\\resources"; Flags: recursesubdirs
Source: "dist\\{self.app_name}.ico"; DestDir: "{{app}}"; DestName: "app.ico"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{self.app_name}"; Filename: "{{app}}\\{self.app_name}.exe"
Name: "{{group}}\\Uninstall {self.app_name}"; Filename: "{{uninstallexe}}"
Name: "{{userdesktop}}\\{self.app_name}"; Filename: "{{app}}\\{self.app_name}.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{self.app_name}.exe"; Description: "Launch {self.app_name}"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{app}}\\products.db"
Type: filesandordirs; Name: "{{app}}\\product_images"
"""
        
        with open('installer.iss', 'w') as f:
            f.write(iss_script)
        
        # Run Inno Setup
        try:
            print("   Running Inno Setup...")
            subprocess.run([inno_exe, 'installer.iss'], check=True)
            
            installer_path = f"dist/{self.app_name}_Setup_v{self.version}.exe"
            if os.path.exists(installer_path):
                size_mb = os.path.getsize(installer_path) / (1024 * 1024)
                print(f"✅ Installer created successfully!")
                print(f"   Location: {installer_path}")
                print(f"   Size: {size_mb:.2f} MB")
                return True
            else:
                print("❌ Installer not found after build!")
                return False
                
        except Exception as e:
            print(f"❌ Installer creation failed: {e}")
            return False
    
    def create_portable_version(self):
        """Create a portable version"""
        print("\n📦 Creating portable version...")
        
        portable_dir = f"dist/{self.app_name}_Portable_v{self.version}"
        if os.path.exists(portable_dir):
            shutil.rmtree(portable_dir)
        os.makedirs(portable_dir)
        
        # Copy executable
        exe_path = f"dist/{self.app_name}.exe"
        if os.path.exists(exe_path):
            shutil.copy(exe_path, f"{portable_dir}/{self.app_name}.exe")
        
        # Copy resources
        if os.path.exists("src/resources"):
            shutil.copytree("src/resources", f"{portable_dir}/resources")
        
        # Copy documentation
        for file in ["README.md", "LICENSE"]:
            if os.path.exists(file):
                shutil.copy(file, f"{portable_dir}/{file}")
        
        # Create launcher
        with open(f"{portable_dir}/Run_Portable.bat", 'w') as f:
            f.write(f"""@echo off
echo ========================================
echo {self.app_name} - Portable Version
echo ========================================
echo.
echo Starting {self.app_name}...
echo Database will be created in the current folder.
echo.
start "" "{self.app_name}.exe"
""")
        
        print(f"✅ Portable version created: {portable_dir}")
        return True
    
    def publish_all(self):
        """Build and publish everything"""
        print("=" * 60)
        print(f"🚀 Publishing {self.app_name} v{self.version}")
        print("=" * 60)
        
        # Clean
        self.clean()
        
        # Build executable
        if not self.build_exe():
            print("\n❌ Build failed. Please fix errors and try again.")
            print("\nCommon issues:")
            print("  1. Make sure src/main.py exists")
            print("  2. Check that all imports are correct")
            print("  3. Verify Python version (3.8+)")
            return
        
        # Create portable version
        self.create_portable_version()
        
        # Create installer
        self.create_installer()
        
        print("\n" + "=" * 60)
        print("🎉 Publishing Complete!")
        print("=" * 60)
        print(f"\n📁 Output folder: {self.output_dir}")
        print("\nFiles created:")
        if os.path.exists(f"dist/{self.app_name}.exe"):
            print(f"  ✅ {self.app_name}.exe - Standalone executable")
        if os.path.exists(f"dist/{self.app_name}_Setup_v{self.version}.exe"):
            print(f"  ✅ {self.app_name}_Setup_v{self.version}.exe - Installer")
        if os.path.exists(f"dist/{self.app_name}_Portable_v{self.version}"):
            print(f"  ✅ Portable version - {self.app_name}_Portable_v{self.version}/")
        
        print("\n📋 Next Steps:")
        print("  1. Test the application on a clean system")
        print("  2. Upload to your website/download portal")
        print("  3. Distribute to customers")
        print("  4. Collect feedback and iterate")

if __name__ == "__main__":
    publisher = PublishManager()
    publisher.publish_all()