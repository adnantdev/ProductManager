# StockPilot - Professional Product Management System

![StockPilot](src/resources/icons/banner.png)

## 🚀 Overview

StockPilot is a comprehensive, desktop-based product management system designed for businesses of all sizes. It provides an intuitive interface for managing products, inventory, suppliers, and transactions with powerful features and real-time analytics.

## ✨ Features

### 📦 Product Management
- Full CRUD operations with image support
- Barcode scanning and generation
- Stock quantity tracking with low-stock alerts
- Active/Inactive product toggling
- Advanced search and filtering by category, supplier, status

### 📊 Inventory Operations
- Stock In/Out logging (receive shipments, record sales)
- Stock adjustments with audit trail
- Barcode lookup/scan-to-find
- Complete transaction history

### 🏢 Supplier Management
- Supplier directory with contact information
- Link suppliers to products
- Product count per supplier

### 📈 Dashboard & Analytics
- Real-time statistics (total SKUs, inventory value, low-stock count)
- Interactive charts (category distribution, stock status)
- Recent transactions display

### 📤 Import/Export
- Bulk import from Excel/CSV files
- Template download for easy data entry
- Export to CSV with all product data

### 📝 Reporting
- Low stock report
- Inventory value report
- Supplier report
- Transaction history

## 📋 Requirements

### Windows
- Windows 7 or later
- 2GB RAM minimum (4GB recommended)
- 100MB free disk space

### macOS
- macOS 10.14 or later
- 2GB RAM minimum (4GB recommended)
- 100MB free disk space

### Linux
- Ubuntu 18.04 or later / similar distros
- 2GB RAM minimum (4GB recommended)
- 100MB free disk space

## 🚀 Quick Start

### Installation

#### Windows
1. Download `StockPilot_Setup.exe`
2. Run the installer
3. Follow the on-screen instructions
4. Launch from Start Menu or Desktop shortcut

#### macOS
1. Download `StockPilot.dmg`
2. Drag to Applications folder
3. Launch from Applications

#### Linux
1. Download `StockPilot.AppImage`
2. Make executable: `chmod +x StockPilot.AppImage`
3. Run: `./StockPilot.AppImage`

### First Run

1. The application will create a default database
2. Add your first product using the "Add Product" button
3. Start managing your inventory!

## 💡 Usage Guide

### Adding a Product
1. Click "Add Product" or press `Ctrl+N`
2. Fill in product details (Name, Price, Quantity, etc.)
3. Upload an image (optional)
4. Click "Save Product"

### Importing Products from Excel
1. Go to the "Import Data" tab
2. Click "Download Template" for the correct format
3. Fill in your product data
4. Click "Choose File" and select your file
5. Preview the data and click "Import Products"

### Managing Stock
1. Go to the "Inventory Ops" tab
2. Select a product
3. Use Add Stock, Remove Stock, or Adjust Stock
4. Add reference and notes for tracking

### Barcode Scanning
- Use the barcode field in the toolbar
- Scan or manually enter a barcode
- The system will find and display the product

## 🔧 Configuration

### Database Location
The database is stored at: `%APPDATA%/StockPilot/products.db`

### Backup
Regular backups are recommended:
1. Copy the `products.db` file to a safe location
2. Use the export feature to create CSV backups

## 🛠️ Troubleshooting

### Application won't start
- Check if your system meets the requirements
- Try running as administrator
- Check the error log in `%APPDATA%/StockPilot/error.log`

### Database issues
- The database file may be corrupted
- Restore from a backup
- Or delete the database and start fresh (all data will be lost)

### Import fails
- Check the file format (must match the template)
- Ensure all required columns are present
- Check for invalid data (e.g., letters in price fields)

## 📊 Support

### Documentation
Full documentation is available at: https://muhammadadnant.vercel.app

### FAQ
Common issues and solutions: https://muhammadadnant.vercel.app

### Contact
- Email: support@yourcompany.com
- Phone: +1-555-123-4567
- Hours: Mon-Fri, 9AM-5PM EST

## 🔒 License

This software is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- Built with Python, PyQt5, and SQLite
- Icons from Font Awesome
- Charts from PyQtChart

---

**StockPilot v1.0** - Made with ❤️ by Your Company