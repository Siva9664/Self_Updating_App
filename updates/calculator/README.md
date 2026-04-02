# Calculator Module v1.0

A comprehensive calculator module for the Self-Updating Calculator App that demonstrates auto-update capabilities.

## 🎯 Features

- **Basic Arithmetic**: Addition, subtraction, multiplication, division
- **Decimal Support**: Precise floating-point calculations
- **History Tracking**: Stores calculation history with clickable recall
- **Keyboard Shortcuts**: Full keyboard input support
- **Error Handling**: Graceful error recovery with user feedback
- **Responsive UI**: Works on all screen sizes

## 🔧 Technical Details

- **Version**: 1.0
- **Dependencies**: None (pure JavaScript implementation)
- **Update Method**: Automatic download via ZIP from update server
- **Storage**: Calculation history stored in browser session

## 🚀 Deployment Information

This calculator module serves as the base functionality for the self-updating application. Future updates can add:

- Scientific functions (sin, cos, tan, log)
- Unit conversions (currency, temperature, distance)
- Memory functions (M+, M-, MR, MC)
- Custom themes and UI enhancements
- Advanced mathematical operations

## 📦 Update Process

The calculator can be updated by:

1. Modifying files in `updates/calculator/`
2. Updating version number in `updates/version.json`
3. Restarting the update server

The app will automatically detect and install calculator updates during its regular 5-minute check cycles.

## 🎮 Usage

The calculator supports:
- **Button clicks** for all operations
- **Keyboard input** (numbers, operators, Enter for equals)
- **History navigation** by clicking previous calculations
- **Clear functions** (C for full clear, ⌫ for backspace)

## 🔄 Auto-Update Demo

This module demonstrates the full auto-update workflow:
- Version checking every 5 minutes
- Automatic download and installation
- Seamless integration without user intervention
- Real-time status feedback

Perfect example of how desktop apps can maintain themselves automatically!
