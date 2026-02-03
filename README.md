# NetCaster 2.0.0

Duplication macros for item exploits using Xbox controller emulation and network packet manipulation.

## Quick Overview

NetCaster is a Windows automation tool that provides:
- **Keydoor Method** - Key duplication using Xbox controller emulation
- **Throwable Dupe** - Throwable item duplication with auto-loop
- **Triggernade Dupe** - Triggernade duplication with inventory drop
- **E-Spam Collection** - Rapid E key spam for item pickup
- **Manual Disconnect** - Toggle packet drop (inbound/outbound)

## Project Organization

This project is now organized into clear, logical directories:

```
NetCaster-2.0.0/
├── src/              # Python source code
├── assets/           # Icons and screenshots
├── build/            # Build configuration
├── dependencies/     # External libraries & drivers
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

**For detailed structure information, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**

## Quick Start

### Running from Source
```powershell
pip install -r requirements.txt
python src/main.py  # Run as Administrator
```

### Building Executable
```powershell
pip install pyinstaller
pyinstaller build/Main.spec
# Output: dist/NetCaster.exe
```

### Using the Build Script
```powershell
python build/build.py
```
The build script generates a unique signature for your build and handles the compilation automatically.

## Requirements

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Privileges**: Administrator (required for WinDivert)
- **Driver**: ViGEmBus (auto-installs on first run)

## Documentation

- **User Guide**: `docs/README.md` - Features and usage
- **Build Instructions**: `docs/BUILD.md` - Compilation guide
- **Development Status**: `docs/Current_status.md` - Version history
- **Project Structure**: `PROJECT_STRUCTURE.md` - Detailed directory layout

## Important Notes

- Press **ESC** to stop all macros
- Triggernade drop position can be recorded for your screen resolution
- For version 1.5.2+: Directional PNG files are required (in `assets/screenshots/`)

## Dependencies

### WinDivert (Packet Filtering)
Located in `dependencies/windivert/`
- Required for network packet manipulation
- Needs administrator rights

### ViGEmBus (Controller Emulation)
Located in `dependencies/drivers/`
- Required for Xbox controller emulation
- Installs on first run

## License

See individual dependency licenses in their respective folders.
