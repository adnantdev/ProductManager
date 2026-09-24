# main.py - Complete Production Version
import sys
import os
import shutil
import csv
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QPieSlice

from database import Database

class ProductManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_product_id = None
        self.image_path = None
        self.images_dir = "product_images"
        self.current_supplier_id = None
        
        # Create images directory if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            
        self.init_ui()
        self.load_products()
        self.load_suppliers()
        self.update_dashboard()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Product Management System v3.0")
        self.setGeometry(100, 100, 1600, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #ddd;
            }
            QMenuBar::item {
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton#danger {
                background-color: #f44336;
            }
            QPushButton#danger:hover {
                background-color: #d32f2f;
            }
            QPushButton#success {
                background-color: #4CAF50;
            }
            QPushButton#success:hover {
                background-color: #388E3C;
            }
            QPushButton#warning {
                background-color: #FF9800;
            }
            QPushButton#warning:hover {
                background-color: #F57C00;
            }
            QPushButton#info {
                background-color: #9C27B0;
            }
            QPushButton#info:hover {
                background-color: #7B1FA2;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e0e0e0;
                selection-background-color: #BBDEFB;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #e3f2fd;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2196F3;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel#image_label {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #fafafa;
                min-height: 200px;
                min-width: 200px;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #333;
            }
        """)
        
        # Central widget with tab layout
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)
        
        # Create tabs
        self.dashboard_tab = QWidget()
        self.products_tab = QWidget()
        self.add_edit_tab = QWidget()
        self.suppliers_tab = QWidget()
        self.inventory_tab = QWidget()
        self.import_tab = QWidget()
        self.transactions_tab = QWidget()
        self.reports_tab = QWidget()
        
        central_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        central_widget.addTab(self.products_tab, "📦 Products")
        central_widget.addTab(self.add_edit_tab, "✏️ Add/Edit Product")
        central_widget.addTab(self.suppliers_tab, "🏢 Suppliers")
        central_widget.addTab(self.inventory_tab, "📦 Inventory Ops")
        central_widget.addTab(self.import_tab, "📥 Import Data")
        central_widget.addTab(self.transactions_tab, "📝 Transactions")
        central_widget.addTab(self.reports_tab, "📈 Reports")
        
        # Setup each tab
        self.setup_dashboard()
        self.setup_products_tab()
        self.setup_add_edit_tab()
        self.setup_suppliers_tab()
        self.setup_inventory_tab()
        self.setup_import_tab()
        self.setup_transactions_tab()
        self.setup_reports_tab()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New Product", self)
        new_action.triggered.connect(lambda: self.switch_to_tab(2))
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("Import from Excel/CSV", self)
        import_action.triggered.connect(lambda: self.switch_to_tab(5))
        import_action.setShortcut("Ctrl+I")
        file_menu.addAction(import_action)
        
        export_action = QAction("Export to CSV", self)
        export_action.triggered.connect(self.export_csv)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        refresh_action.setShortcut("F5")
        view_menu.addAction(refresh_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("Reports")
        reports_menu.addAction("Low Stock Report", self.show_low_stock_report)
        reports_menu.addAction("Value Report", self.show_value_report)
        reports_menu.addAction("Supplier Report", self.show_supplier_report)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # Add actions
        add_action = QAction("➕ Add Product", self)
        add_action.triggered.connect(lambda: self.switch_to_tab(2))
        toolbar.addAction(add_action)
        
        import_action = QAction("📥 Import", self)
        import_action.triggered.connect(lambda: self.switch_to_tab(5))
        toolbar.addAction(import_action)
        
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Barcode scanner input
        toolbar.addWidget(QLabel("🔍 Barcode:"))
        barcode_input = QLineEdit()
        barcode_input.setPlaceholderText("Scan or enter barcode...")
        barcode_input.setMaximumWidth(200)
        barcode_input.returnPressed.connect(lambda: self.lookup_barcode(barcode_input.text()))
        toolbar.addWidget(barcode_input)
        self.barcode_input = barcode_input
        
        toolbar.addSeparator()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search products...")
        search_input.setMaximumWidth(300)
        search_input.textChanged.connect(self.search_products)
        toolbar.addWidget(search_input)
        self.search_input = search_input
    
    # ============ Dashboard ============
    
    def setup_dashboard(self):
        """Setup the dashboard tab"""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Header
        header = QLabel("📊 Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        self.stats_cards = {}
        stats_data = [
            ('total_products', 'Total SKUs', '📦'),
            ('total_value', 'Inventory Value', '💰'),
            ('low_stock', 'Low Stock Items', '⚠️'),
            ('out_of_stock', 'Out of Stock', '🚫'),
            ('total_suppliers', 'Suppliers', '🏢'),
            ('recent_transactions', 'Recent Transactions', '📝')
        ]
        
        for key, label, icon in stats_data:
            card = QGroupBox()
            card_layout = QVBoxLayout()
            
            label_widget = QLabel(f"{icon} {label}")
            label_widget.setStyleSheet("font-size: 14px; color: #666;")
            
            value_widget = QLabel("0")
            value_widget.setStyleSheet("font-size: 24px; font-weight: bold;")
            value_widget.setObjectName(f"stats_{key}")
            
            card_layout.addWidget(label_widget)
            card_layout.addWidget(value_widget)
            card_layout.addStretch()
            card.setLayout(card_layout)
            card.setMaximumHeight(100)
            
            stats_layout.addWidget(card)
            self.stats_cards[key] = value_widget
        
        layout.addLayout(stats_layout)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Category chart
        category_chart_group = QGroupBox("Products by Category")
        category_chart_group.setLayout(QVBoxLayout())
        self.category_chart_view = QChartView()
        self.category_chart_view.setRenderHint(QPainter.Antialiasing)
        category_chart_group.layout().addWidget(self.category_chart_view)
        charts_layout.addWidget(category_chart_group)
        
        # Stock status chart
        stock_chart_group = QGroupBox("Stock Status")
        stock_chart_group.setLayout(QVBoxLayout())
        self.stock_chart_view = QChartView()
        self.stock_chart_view.setRenderHint(QPainter.Antialiasing)
        stock_chart_group.layout().addWidget(self.stock_chart_view)
        charts_layout.addWidget(stock_chart_group)
        
        layout.addLayout(charts_layout)
        
        # Recent transactions
        recent_group = QGroupBox("Recent Transactions")
        recent_group.setLayout(QVBoxLayout())
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(6)
        self.recent_transactions_table.setHorizontalHeaderLabels([
            "Product", "Type", "Quantity", "Previous", "New", "Date"
        ])
        self.recent_transactions_table.horizontalHeader().setStretchLastSection(True)
        recent_group.layout().addWidget(self.recent_transactions_table)
        
        layout.addWidget(recent_group)
    
    # ============ Products Tab ============
    
    def setup_products_tab(self):
        """Setup the products list tab"""
        layout = QVBoxLayout(self.products_tab)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.load_products)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Out of Stock", "Discontinued"])
        self.status_filter.currentTextChanged.connect(self.load_products)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Supplier:"))
        self.supplier_filter = QComboBox()
        self.supplier_filter.addItem("All Suppliers")
        self.supplier_filter.currentTextChanged.connect(self.load_products)
        filter_layout.addWidget(self.supplier_filter)
        
        filter_layout.addStretch()
        
        # Add product button
        add_btn = QPushButton("➕ Add New Product")
        add_btn.clicked.connect(lambda: self.switch_to_tab(2))
        add_btn.setObjectName("success")
        filter_layout.addWidget(add_btn)
        
        # Toggle inactive
        self.show_inactive_check = QCheckBox("Show Inactive")
        self.show_inactive_check.stateChanged.connect(self.load_products)
        filter_layout.addWidget(self.show_inactive_check)
        
        layout.addLayout(filter_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(11)
        self.products_table.setHorizontalHeaderLabels([
            "Image", "ID", "Name", "Category", "Price", "Quantity", 
            "Min Qty", "Status", "Supplier", "Active", "Actions"
        ])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.products_table)
    
    # ============ Add/Edit Tab ============
    
    def setup_add_edit_tab(self):
        """Setup the add/edit product tab"""
        layout = QVBoxLayout(self.add_edit_tab)
        
        # Split into two columns: form and image preview
        main_split = QHBoxLayout()
        
        # Left side: Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        
        form_grid = QFormLayout(scroll_widget)
        form_grid.setSpacing(10)
        
        # Basic information
        self.product_id_label = QLabel("New Product")
        self.product_id_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        form_grid.addRow("", self.product_id_label)
        
        self.name_input = QLineEdit()
        form_grid.addRow("Name:*", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form_grid.addRow("Description:", self.description_input)
        
        # Price and quantity
        price_qty_layout = QHBoxLayout()
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setPrefix("$ ")
        price_qty_layout.addWidget(QLabel("Price:*"))
        price_qty_layout.addWidget(self.price_input)
        
        price_qty_layout.addSpacing(20)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 999999)
        price_qty_layout.addWidget(QLabel("Quantity:*"))
        price_qty_layout.addWidget(self.quantity_input)
        
        form_grid.addRow("", price_qty_layout)
        
        # Category and supplier
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        form_grid.addRow("Category:*", self.category_input)
        
        self.supplier_input = QComboBox()
        self.supplier_input.setEditable(True)
        form_grid.addRow("Supplier:", self.supplier_input)
        
        # Additional fields
        self.min_qty_input = QSpinBox()
        self.min_qty_input.setRange(0, 9999)
        self.min_qty_input.setValue(5)
        form_grid.addRow("Minimum Quantity:", self.min_qty_input)
        
        # Barcode and weight
        extra_layout = QHBoxLayout()
        
        self.barcode_input = QLineEdit()
        extra_layout.addWidget(QLabel("Barcode:"))
        extra_layout.addWidget(self.barcode_input)
        
        extra_layout.addSpacing(20)
        
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 9999)
        self.weight_input.setSuffix(" kg")
        extra_layout.addWidget(QLabel("Weight:"))
        extra_layout.addWidget(self.weight_input)
        
        form_grid.addRow("", extra_layout)
        
        self.dimensions_input = QLineEdit()
        form_grid.addRow("Dimensions:", self.dimensions_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form_grid.addRow("Notes:", self.notes_input)
        
        # Image upload
        image_upload_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("📸 Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)
        self.upload_btn.setObjectName("success")
        image_upload_layout.addWidget(self.upload_btn)
        
        self.remove_image_btn = QPushButton("🗑️ Remove Image")
        self.remove_image_btn.clicked.connect(self.remove_image)
        self.remove_image_btn.setObjectName("danger")
        image_upload_layout.addWidget(self.remove_image_btn)
        
        form_grid.addRow("Product Image:", image_upload_layout)
        
        form_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save Product")
        self.save_btn.setObjectName("success")
        self.save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        form_layout.addLayout(button_layout)
        
        # Right side: Image preview
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        image_label = QLabel("Product Image Preview")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setObjectName("image_label")
        image_label.setMinimumSize(300, 300)
        self.image_preview_label = image_label
        
        image_layout.addWidget(QLabel("Image Preview:"))
        image_layout.addWidget(image_label)
        image_layout.addStretch()
        
        # Add both sides to split
        main_split.addWidget(form_widget, 2)
        main_split.addWidget(image_widget, 1)
        
        layout.addLayout(main_split)
        
        # Connect quantity change
        self.quantity_input.valueChanged.connect(self.auto_update_status)
    
    # ============ Suppliers Tab ============
    
    def setup_suppliers_tab(self):
        """Setup the suppliers tab"""
        layout = QVBoxLayout(self.suppliers_tab)
        
        # Header with add button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🏢 Supplier Directory"))
        header_layout.addStretch()
        
        add_supplier_btn = QPushButton("➕ Add Supplier")
        add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)
        add_supplier_btn.setObjectName("success")
        header_layout.addWidget(add_supplier_btn)
        
        layout.addLayout(header_layout)
        
        # Supplier search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.supplier_search = QLineEdit()
        self.supplier_search.setPlaceholderText("Search suppliers...")
        self.supplier_search.textChanged.connect(self.load_suppliers)
        search_layout.addWidget(self.supplier_search)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(8)
        self.suppliers_table.setHorizontalHeaderLabels([
            "ID", "Name", "Contact Person", "Email", "Phone", 
            "Products", "Created", "Actions"
        ])
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.setAlternatingRowColors(True)
        layout.addWidget(self.suppliers_table)
    
    # ============ Inventory Ops Tab ============
    
    def setup_inventory_tab(self):
        """Setup the inventory operations tab"""
        layout = QVBoxLayout(self.inventory_tab)
        
        # Header
        header = QLabel("📦 Inventory Operations")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Product selection
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Select Product:"))
        
        self.inventory_product_combo = QComboBox()
        self.inventory_product_combo.setEditable(True)
        self.inventory_product_combo.setMinimumWidth(300)
        select_layout.addWidget(self.inventory_product_combo)
        
        # Barcode lookup
        select_layout.addWidget(QLabel("or Barcode:"))
        self.inventory_barcode_input = QLineEdit()
        self.inventory_barcode_input.setPlaceholderText("Scan barcode...")
        self.inventory_barcode_input.setMaximumWidth(150)
        self.inventory_barcode_input.returnPressed.connect(self.inventory_barcode_lookup)
        select_layout.addWidget(self.inventory_barcode_input)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Product info display
        self.inventory_info_group = QGroupBox("Product Information")
        info_layout = QGridLayout()
        
        self.inv_name_label = QLabel("-")
        self.inv_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(QLabel("Name:"), 0, 0)
        info_layout.addWidget(self.inv_name_label, 0, 1)
        
        self.inv_sku_label = QLabel("-")
        info_layout.addWidget(QLabel("SKU:"), 0, 2)
        info_layout.addWidget(self.inv_sku_label, 0, 3)
        
        self.inv_current_qty_label = QLabel("0")
        self.inv_current_qty_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        info_layout.addWidget(QLabel("Current Stock:"), 1, 0)
        info_layout.addWidget(self.inv_current_qty_label, 1, 1)
        
        self.inv_min_qty_label = QLabel("0")
        info_layout.addWidget(QLabel("Min Quantity:"), 1, 2)
        info_layout.addWidget(self.inv_min_qty_label, 1, 3)
        
        self.inv_price_label = QLabel("$0.00")
        info_layout.addWidget(QLabel("Price:"), 2, 0)
        info_layout.addWidget(self.inv_price_label, 2, 1)
        
        self.inv_supplier_label = QLabel("-")
        info_layout.addWidget(QLabel("Supplier:"), 2, 2)
        info_layout.addWidget(self.inv_supplier_label, 2, 3)
        
        self.inventory_info_group.setLayout(info_layout)
        layout.addWidget(self.inventory_info_group)
        
        # Stock operations
        ops_group = QGroupBox("Stock Operations")
        ops_layout = QGridLayout()
        
        # Add stock
        ops_layout.addWidget(QLabel("Add Stock:"), 0, 0)
        self.add_stock_qty = QSpinBox()
        self.add_stock_qty.setRange(1, 99999)
        self.add_stock_qty.setValue(10)
        ops_layout.addWidget(self.add_stock_qty, 0, 1)
        
        self.add_stock_btn = QPushButton("➕ Receive Stock")
        self.add_stock_btn.clicked.connect(self.add_stock_action)
        self.add_stock_btn.setObjectName("success")
        ops_layout.addWidget(self.add_stock_btn, 0, 2)
        
        # Remove stock
        ops_layout.addWidget(QLabel("Remove Stock:"), 1, 0)
        self.remove_stock_qty = QSpinBox()
        self.remove_stock_qty.setRange(1, 99999)
        self.remove_stock_qty.setValue(1)
        ops_layout.addWidget(self.remove_stock_qty, 1, 1)
        
        self.remove_stock_btn = QPushButton("➖ Remove Stock")
        self.remove_stock_btn.clicked.connect(self.remove_stock_action)
        self.remove_stock_btn.setObjectName("danger")
        ops_layout.addWidget(self.remove_stock_btn, 1, 2)
        
        # Adjust stock
        ops_layout.addWidget(QLabel("Adjust To:"), 2, 0)
        self.adjust_stock_qty = QSpinBox()
        self.adjust_stock_qty.setRange(0, 99999)
        ops_layout.addWidget(self.adjust_stock_qty, 2, 1)
        
        self.adjust_stock_btn = QPushButton("📊 Adjust Stock")
        self.adjust_stock_btn.clicked.connect(self.adjust_stock_action)
        self.adjust_stock_btn.setObjectName("warning")
        ops_layout.addWidget(self.adjust_stock_btn, 2, 2)
        
        # Reference/Notes
        ops_layout.addWidget(QLabel("Reference:"), 3, 0)
        self.inv_reference = QLineEdit()
        self.inv_reference.setPlaceholderText("Order #, Sale #, etc.")
        ops_layout.addWidget(self.inv_reference, 3, 1, 1, 2)
        
        ops_layout.addWidget(QLabel("Notes:"), 4, 0)
        self.inv_notes = QTextEdit()
        self.inv_notes.setMaximumHeight(50)
        ops_layout.addWidget(self.inv_notes, 4, 1, 1, 2)
        
        ops_group.setLayout(ops_layout)
        layout.addWidget(ops_group)
        
        # Recent transactions for selected product
        trans_group = QGroupBox("Recent Transactions")
        trans_group.setLayout(QVBoxLayout())
        
        self.inventory_transactions_table = QTableWidget()
        self.inventory_transactions_table.setColumnCount(6)
        self.inventory_transactions_table.setHorizontalHeaderLabels([
            "Type", "Quantity", "Previous", "New", "Reference", "Date"
        ])
        trans_group.layout().addWidget(self.inventory_transactions_table)
        
        layout.addWidget(trans_group)
    
    # ============ Import Tab ============
    
    def setup_import_tab(self):
        """Setup the import data tab"""
        layout = QVBoxLayout(self.import_tab)
        
        # Header
        header = QLabel("📥 Import Products from Excel/CSV")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Info box
        info_box = QGroupBox("Instructions")
        info_layout = QVBoxLayout()
        info_text = QLabel("""
        <b>How to import products:</b><br><br>
        1. Prepare your Excel (.xlsx, .xls) or CSV file with the following columns:<br>
        &nbsp;&nbsp;&nbsp;• <b>name</b> (required) - Product name<br>
        &nbsp;&nbsp;&nbsp;• <b>price</b> (required) - Product price (number)<br>
        &nbsp;&nbsp;&nbsp;• <b>quantity</b> (required) - Stock quantity (number)<br>
        &nbsp;&nbsp;&nbsp;• <b>category</b> - Product category<br>
        &nbsp;&nbsp;&nbsp;• <b>description</b> - Product description<br>
        &nbsp;&nbsp;&nbsp;• <b>supplier</b> - Supplier name<br>
        &nbsp;&nbsp;&nbsp;• <b>min_quantity</b> - Minimum stock level (default: 5)<br>
        &nbsp;&nbsp;&nbsp;• <b>barcode</b> - Product barcode<br>
        &nbsp;&nbsp;&nbsp;• <b>weight</b> - Product weight<br>
        &nbsp;&nbsp;&nbsp;• <b>dimensions</b> - Product dimensions<br>
        &nbsp;&nbsp;&nbsp;• <b>notes</b> - Additional notes<br><br>
        2. Click "Choose File" to select your file<br>
        3. Preview the data and click "Import Products"<br>
        <br>
        <b>Tip:</b> You can download a sample template to get started!
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_box.setLayout(info_layout)
        layout.addWidget(info_box)
        
        # File selection
        file_group = QGroupBox("Select File")
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        file_layout.addWidget(self.file_path_label, 2)
        
        choose_file_btn = QPushButton("📁 Choose File")
        choose_file_btn.clicked.connect(self.choose_import_file)
        choose_file_btn.setObjectName("success")
        file_layout.addWidget(choose_file_btn)
        
        download_template_btn = QPushButton("📄 Download Template")
        download_template_btn.clicked.connect(self.download_template)
        download_template_btn.setObjectName("warning")
        file_layout.addWidget(download_template_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Preview
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self.preview_table)
        
        self.preview_stats_label = QLabel("No data loaded")
        preview_layout.addWidget(self.preview_stats_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_btn = QPushButton("🚀 Import Products")
        self.import_btn.setObjectName("success")
        self.import_btn.clicked.connect(self.import_products)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)
        
        self.clear_preview_btn = QPushButton("🗑️ Clear Preview")
        self.clear_preview_btn.clicked.connect(self.clear_import_preview)
        button_layout.addWidget(self.clear_preview_btn)
        
        layout.addLayout(button_layout)
        
        # Progress
        self.import_progress = QProgressBar()
        self.import_progress.setVisible(False)
        layout.addWidget(self.import_progress)
        
        layout.addStretch()
    
    # ============ Transactions Tab ============
    
    def setup_transactions_tab(self):
        """Setup the transactions tab"""
        layout = QVBoxLayout(self.transactions_tab)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Product:"))
        self.transaction_product_filter = QComboBox()
        self.transaction_product_filter.addItem("All Products")
        self.transaction_product_filter.currentIndexChanged.connect(self.load_transactions)
        filter_layout.addWidget(self.transaction_product_filter)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.transaction_type_filter = QComboBox()
        self.transaction_type_filter.addItems(["All Types", "RECEIVE", "REMOVE", "INITIAL", "UPDATE", "ADJUST_IN", "ADJUST_OUT"])
        self.transaction_type_filter.currentTextChanged.connect(self.load_transactions)
        filter_layout.addWidget(self.transaction_type_filter)
        
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_transactions)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            "Product", "Type", "Quantity", "Previous", "New", 
            "Reference", "Created By", "Date"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setAlternatingRowColors(True)
        layout.addWidget(self.transactions_table)
    
    # ============ Reports Tab ============
    
    def setup_reports_tab(self):
        """Setup the reports tab"""
        layout = QVBoxLayout(self.reports_tab)
        
        # Report buttons
        button_layout = QHBoxLayout()
        
        low_stock_btn = QPushButton("📋 Low Stock Report")
        low_stock_btn.clicked.connect(self.show_low_stock_report)
        low_stock_btn.setObjectName("warning")
        button_layout.addWidget(low_stock_btn)
        
        value_btn = QPushButton("💰 Value Report")
        value_btn.clicked.connect(self.show_value_report)
        value_btn.setObjectName("success")
        button_layout.addWidget(value_btn)
        
        supplier_btn = QPushButton("🏢 Supplier Report")
        supplier_btn.clicked.connect(self.show_supplier_report)
        supplier_btn.setObjectName("info")
        button_layout.addWidget(supplier_btn)
        
        export_btn = QPushButton("📤 Export All Data")
        export_btn.clicked.connect(self.export_csv)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Report display
        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        self.report_display.setFont(QFont("Courier", 10))
        layout.addWidget(self.report_display)
    
    # ============ Core Functions ============
    
    def refresh_all(self):
        """Refresh all data"""
        self.load_products()
        self.load_suppliers()
        self.update_dashboard()
        self.load_transactions()
        self.statusBar().showMessage("Refreshed", 2000)
    
    def load_products(self):
        """Load products into the table"""
        try:
            category = self.category_filter.currentText()
            if category == "All Categories":
                category = None
            
            status = self.status_filter.currentText()
            if status == "All Status":
                status = None
            
            supplier = self.supplier_filter.currentText()
            supplier_id = None
            if supplier != "All Suppliers" and supplier:
                # Try to get supplier ID
                suppliers = self.db.get_all_suppliers()
                for s in suppliers:
                    if s['name'] == supplier:
                        supplier_id = s['id']
                        break
            
            search = getattr(self, 'search_input', None)
            search_text = search.text() if search else None
            
            include_inactive = self.show_inactive_check.isChecked()
            
            products = self.db.get_all_products(category, search_text, supplier_id, status, include_inactive)
            
            # Update dropdowns
            self.update_product_dropdowns(products)
            
            self.products_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Image
                image_item = self.display_image_in_table(product.get('image_path'))
                self.products_table.setItem(row, 0, image_item)
                
                # Data
                self.products_table.setItem(row, 1, QTableWidgetItem(product['id']))
                self.products_table.setItem(row, 2, QTableWidgetItem(product['name']))
                self.products_table.setItem(row, 3, QTableWidgetItem(product['category']))
                self.products_table.setItem(row, 4, QTableWidgetItem(f"${product['price']:.2f}"))
                
                # Quantity with color coding
                qty_item = QTableWidgetItem(str(product['quantity']))
                if product['quantity'] <= product['min_quantity'] and product['quantity'] > 0:
                    qty_item.setBackground(QColor(255, 235, 59))  # Yellow
                elif product['quantity'] == 0:
                    qty_item.setBackground(QColor(255, 205, 210))  # Red
                self.products_table.setItem(row, 5, qty_item)
                
                self.products_table.setItem(row, 6, QTableWidgetItem(str(product['min_quantity'])))
                self.products_table.setItem(row, 7, QTableWidgetItem(product['status']))
                self.products_table.setItem(row, 8, QTableWidgetItem(product.get('supplier_name', '')))
                
                # Active toggle
                active_check = QCheckBox()
                active_check.setChecked(product.get('is_active', 1) == 1)
                active_check.stateChanged.connect(lambda state, pid=product['id']: self.toggle_product_active(pid, state))
                self.products_table.setCellWidget(row, 9, active_check)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.setToolTip("Edit product")
                edit_btn.clicked.connect(lambda checked, pid=product['id']: self.edit_product(pid))
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setToolTip("Delete product")
                delete_btn.setObjectName("danger")
                delete_btn.clicked.connect(lambda checked, pid=product['id']: self.delete_product(pid))
                
                view_image_btn = QPushButton("🖼️")
                view_image_btn.setFixedSize(30, 30)
                view_image_btn.setToolTip("View image")
                if product.get('image_path'):
                    view_image_btn.clicked.connect(lambda checked, path=product.get('image_path'): self.view_image(path))
                else:
                    view_image_btn.setEnabled(False)
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addWidget(view_image_btn)
                actions_layout.addStretch()
                
                self.products_table.setCellWidget(row, 10, actions_widget)
            
            self.products_table.setColumnWidth(0, 60)
            self.products_table.resizeColumnsToContents()
            
            self.update_dashboard()
            self.statusBar().showMessage(f"Loaded {len(products)} products", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error loading products: {str(e)}", 5000)
    
    def update_product_dropdowns(self, products):
        """Update all product dropdowns"""
        # Inventory product combo
        self.inventory_product_combo.clear()
        for p in products:
            if p.get('is_active', 1) == 1:
                self.inventory_product_combo.addItem(f"{p['name']} ({p['id']})", p['id'])
        
        # Transaction product filter
        self.transaction_product_filter.clear()
        self.transaction_product_filter.addItem("All Products")
        for p in products:
            self.transaction_product_filter.addItem(f"{p['name']} ({p['id']})", p['id'])
    
    def load_suppliers(self):
        """Load suppliers into the table"""
        try:
            search = self.supplier_search.text() if hasattr(self, 'supplier_search') else None
            
            suppliers = self.db.get_all_suppliers(search)
            
            # Update supplier filter
            self.supplier_filter.clear()
            self.supplier_filter.addItem("All Suppliers")
            for s in suppliers:
                self.supplier_filter.addItem(s['name'])
            
            self.suppliers_table.setRowCount(len(suppliers))
            
            for row, supplier in enumerate(suppliers):
                self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier['id'])))
                self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier['name']))
                self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.get('contact_person', '')))
                self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.get('email', '')))
                self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier.get('phone', '')))
                self.suppliers_table.setItem(row, 5, QTableWidgetItem(str(supplier.get('product_count', 0))))
                self.suppliers_table.setItem(row, 6, QTableWidgetItem(supplier['created_at'][:10]))
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, sid=supplier['id']: self.edit_supplier(sid))
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setObjectName("danger")
                delete_btn.clicked.connect(lambda checked, sid=supplier['id']: self.delete_supplier(sid))
                
                view_btn = QPushButton("👁️")
                view_btn.setFixedSize(30, 30)
                view_btn.clicked.connect(lambda checked, sid=supplier['id']: self.view_supplier(sid))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.suppliers_table.setCellWidget(row, 7, actions_widget)
            
            self.suppliers_table.resizeColumnsToContents()
        except Exception as e:
            self.statusBar().showMessage(f"Error loading suppliers: {str(e)}", 5000)
    
    # ============ Product CRUD Operations ============
    
    def save_product(self):
        """Save or update a product"""
        data = {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'price': self.price_input.value(),
            'quantity': self.quantity_input.value(),
            'category': self.category_input.currentText(),
            'supplier_name': self.supplier_input.currentText(),
            'min_quantity': self.min_qty_input.value(),
            'barcode': self.barcode_input.text().strip(),
            'weight': self.weight_input.value(),
            'dimensions': self.dimensions_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip(),
            'image_path': self.image_path
        }
        
        # Validate
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return
        
        if data['price'] <= 0:
            QMessageBox.warning(self, "Validation Error", "Price must be greater than 0!")
            return
        
        try:
            # Get or create supplier
            if data['supplier_name']:
                supplier_id = self.db.get_supplier_id_by_name(data['supplier_name'])
                if not supplier_id:
                    # Create new supplier
                    supplier_id = self.db.add_supplier({'name': data['supplier_name']})
                data['supplier_id'] = supplier_id
            else:
                data['supplier_id'] = None
            
            if self.current_product_id:
                # Update
                success = self.db.update_product(self.current_product_id, data)
                if success:
                    QMessageBox.information(self, "Success", "Product updated successfully!")
                    self.clear_form()
                    self.refresh_all()
                    self.switch_to_tab(0)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update product!")
            else:
                # Add new
                product_id = self.db.add_product(data)
                QMessageBox.information(self, "Success", f"Product added successfully! ID: {product_id}")
                self.clear_form()
                self.refresh_all()
                self.switch_to_tab(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def edit_product(self, product_id):
        """Load product data into the edit form"""
        product = self.db.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "Error", "Product not found!")
            return
        
        self.current_product_id = product_id
        self.product_id_label.setText(f"Editing: {product['name']} (ID: {product_id})")
        
        self.name_input.setText(product['name'])
        self.description_input.setText(product.get('description', ''))
        self.price_input.setValue(product['price'])
        self.quantity_input.setValue(product['quantity'])
        
        # Category
        index = self.category_input.findText(product['category'])
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        else:
            self.category_input.addItem(product['category'])
            self.category_input.setCurrentText(product['category'])
        
        # Supplier
        supplier_name = product.get('supplier_name', '')
        if supplier_name:
            index = self.supplier_input.findText(supplier_name)
            if index >= 0:
                self.supplier_input.setCurrentIndex(index)
            else:
                self.supplier_input.addItem(supplier_name)
                self.supplier_input.setCurrentText(supplier_name)
        
        self.min_qty_input.setValue(product.get('min_quantity', 5))
        self.barcode_input.setText(product.get('barcode', ''))
        self.weight_input.setValue(product.get('weight', 0.0))
        self.dimensions_input.setText(product.get('dimensions', ''))
        self.notes_input.setText(product.get('notes', ''))
        
        # Image
        self.image_path = product.get('image_path')
        if self.image_path and os.path.exists(self.image_path):
            self.display_image(self.image_path)
        else:
            self.image_path = None
            self.image_preview_label.setText("Product Image Preview")
            self.image_preview_label.setStyleSheet("")
        
        self.save_btn.setText("💾 Update Product")
        self.switch_to_tab(2)
    
    def delete_product(self, product_id):
        """Delete a product with confirmation"""
        product = self.db.get_product(product_id)
        if not product:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{product['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_product(product_id, permanent=False):
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.refresh_all()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete product!")
    
    def toggle_product_active(self, product_id, state):
        """Toggle product active status"""
        try:
            active = state == Qt.Checked
            self.db.toggle_product_active(product_id, active)
            status = "activated" if active else "deactivated"
            self.statusBar().showMessage(f"Product {status}", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle status: {str(e)}")
            self.load_products()
    
    def clear_form(self):
        """Clear the add/edit form"""
        self.current_product_id = None
        self.product_id_label.setText("New Product")
        self.name_input.clear()
        self.description_input.clear()
        self.price_input.setValue(0)
        self.quantity_input.setValue(0)
        self.category_input.setCurrentIndex(0)
        self.supplier_input.setCurrentText("")
        self.min_qty_input.setValue(5)
        self.barcode_input.clear()
        self.weight_input.setValue(0)
        self.dimensions_input.clear()
        self.notes_input.clear()
        
        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except:
                pass
        self.image_path = None
        self.image_preview_label.setText("Product Image Preview")
        self.image_preview_label.setStyleSheet("")
        
        self.save_btn.setText("💾 Save Product")
    
    def auto_update_status(self):
        """Auto-update status based on quantity"""
        quantity = self.quantity_input.value()
        if quantity == 0:
            self.quantity_input.setStyleSheet("background-color: #ffcdd2;")
        else:
            self.quantity_input.setStyleSheet("")
    
    # ============ Supplier Operations ============
    
    def show_add_supplier_dialog(self):
        """Show add supplier dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Supplier")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        name_input = QLineEdit()
        form.addRow("Name:*", name_input)
        
        contact_input = QLineEdit()
        form.addRow("Contact Person:", contact_input)
        
        email_input = QLineEdit()
        form.addRow("Email:", email_input)
        
        phone_input = QLineEdit()
        form.addRow("Phone:", phone_input)
        
        address_input = QTextEdit()
        address_input.setMaximumHeight(80)
        form.addRow("Address:", address_input)
        
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(60)
        form.addRow("Notes:", notes_input)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save Supplier")
        save_btn.setObjectName("success")
        cancel_btn = QPushButton("Cancel")
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def save_supplier():
            try:
                data = {
                    'name': name_input.text().strip(),
                    'contact_person': contact_input.text().strip(),
                    'email': email_input.text().strip(),
                    'phone': phone_input.text().strip(),
                    'address': address_input.toPlainText().strip(),
                    'notes': notes_input.toPlainText().strip()
                }
                
                if not data['name']:
                    QMessageBox.warning(dialog, "Validation Error", "Supplier name is required!")
                    return
                
                supplier_id = self.db.add_supplier(data)
                QMessageBox.information(dialog, "Success", f"Supplier added successfully! ID: {supplier_id}")
                dialog.accept()
                self.load_suppliers()
                self.load_products()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        save_btn.clicked.connect(save_supplier)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def edit_supplier(self, supplier_id):
        """Edit supplier"""
        supplier = self.db.get_supplier(supplier_id)
        if not supplier:
            QMessageBox.warning(self, "Error", "Supplier not found!")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Supplier: {supplier['name']}")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        name_input = QLineEdit(supplier['name'])
        form.addRow("Name:*", name_input)
        
        contact_input = QLineEdit(supplier.get('contact_person', ''))
        form.addRow("Contact Person:", contact_input)
        
        email_input = QLineEdit(supplier.get('email', ''))
        form.addRow("Email:", email_input)
        
        phone_input = QLineEdit(supplier.get('phone', ''))
        form.addRow("Phone:", phone_input)
        
        address_input = QTextEdit(supplier.get('address', ''))
        address_input.setMaximumHeight(80)
        form.addRow("Address:", address_input)
        
        notes_input = QTextEdit(supplier.get('notes', ''))
        notes_input.setMaximumHeight(60)
        form.addRow("Notes:", notes_input)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Update Supplier")
        save_btn.setObjectName("success")
        cancel_btn = QPushButton("Cancel")
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def update_supplier():
            try:
                data = {
                    'name': name_input.text().strip(),
                    'contact_person': contact_input.text().strip(),
                    'email': email_input.text().strip(),
                    'phone': phone_input.text().strip(),
                    'address': address_input.toPlainText().strip(),
                    'notes': notes_input.toPlainText().strip()
                }
                
                if not data['name']:
                    QMessageBox.warning(dialog, "Validation Error", "Supplier name is required!")
                    return
                
                self.db.update_supplier(supplier_id, data)
                QMessageBox.information(dialog, "Success", "Supplier updated successfully!")
                dialog.accept()
                self.load_suppliers()
                self.load_products()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        save_btn.clicked.connect(update_supplier)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def delete_supplier(self, supplier_id):
        """Delete supplier with confirmation"""
        supplier = self.db.get_supplier(supplier_id)
        if not supplier:
            return
        
        try:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete supplier '{supplier['name']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.db.delete_supplier(supplier_id, permanent=False)
                QMessageBox.information(self, "Success", "Supplier deleted successfully!")
                self.load_suppliers()
                self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def view_supplier(self, supplier_id):
        """View supplier details"""
        supplier = self.db.get_supplier(supplier_id)
        if not supplier:
            return
        
        # Get products from this supplier
        products = self.db.get_all_products(supplier_id=supplier_id)
        
        msg = f"""
        <h2>Supplier Details</h2>
        <b>Name:</b> {supplier['name']}<br>
        <b>Contact Person:</b> {supplier.get('contact_person', 'N/A')}<br>
        <b>Email:</b> {supplier.get('email', 'N/A')}<br>
        <b>Phone:</b> {supplier.get('phone', 'N/A')}<br>
        <b>Address:</b> {supplier.get('address', 'N/A')}<br>
        <b>Products:</b> {len(products)}<br>
        <b>Created:</b> {supplier['created_at']}<br>
        <b>Notes:</b> {supplier.get('notes', 'N/A')}<br>
        <br>
        <h3>Products from this supplier:</h3>
        """
        
        if products:
            msg += "<ul>"
            for p in products[:10]:
                msg += f"<li>{p['name']} - ${p['price']:.2f} (Qty: {p['quantity']})</li>"
            if len(products) > 10:
                msg += f"<li>... and {len(products) - 10} more</li>"
            msg += "</ul>"
        else:
            msg += "<i>No products from this supplier</i>"
        
        QMessageBox.about(self, f"Supplier: {supplier['name']}", msg)
    
    # ============ Inventory Operations ============
    
    def inventory_barcode_lookup(self):
        """Lookup product by barcode in inventory tab"""
        barcode = self.inventory_barcode_input.text().strip()
        if barcode:
            self.lookup_barcode(barcode)
            self.inventory_barcode_input.clear()
    
    def lookup_barcode(self, barcode):
        """Lookup product by barcode"""
        product = self.db.get_product_by_barcode(barcode)
        if product:
            # Select in dropdown
            for i in range(self.inventory_product_combo.count()):
                if self.inventory_product_combo.itemData(i) == product['id']:
                    self.inventory_product_combo.setCurrentIndex(i)
                    self.load_inventory_product(product['id'])
                    self.statusBar().showMessage(f"Found: {product['name']}", 3000)
                    return
        
        # Try searching by name
        products = self.db.get_all_products(search=barcode)
        if products:
            # Show search results
            items = [f"{p['name']} ({p['id']})" for p in products]
            item, ok = QInputDialog.getItem(
                self, "Multiple Matches", 
                f"Found {len(products)} products matching '{barcode}'. Select one:",
                items, 0, False
            )
            if ok and item:
                product_id = item.split('(')[-1].rstrip(')')
                self.inventory_product_combo.setCurrentText(item)
                self.load_inventory_product(product_id)
        else:
            QMessageBox.information(self, "Not Found", f"No product found with barcode: {barcode}")
    
    def load_inventory_product(self, product_id):
        """Load product details in inventory tab"""
        product = self.db.get_product(product_id)
        if not product:
            return
        
        self.inv_name_label.setText(product['name'])
        self.inv_sku_label.setText(product['id'])
        self.inv_current_qty_label.setText(str(product['quantity']))
        self.inv_min_qty_label.setText(str(product['min_quantity']))
        self.inv_price_label.setText(f"${product['price']:.2f}")
        self.inv_supplier_label.setText(product.get('supplier_name', 'N/A'))
        
        # Color coding for quantity
        if product['quantity'] <= product['min_quantity'] and product['quantity'] > 0:
            self.inv_current_qty_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800;")
        elif product['quantity'] == 0:
            self.inv_current_qty_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f44336;")
        else:
            self.inv_current_qty_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        
        # Load transactions for this product
        self.load_inventory_transactions(product_id)
    
    def load_inventory_transactions(self, product_id):
        """Load inventory transactions for a product"""
        transactions = self.db.get_inventory_transactions(product_id, limit=20)
        
        self.inventory_transactions_table.setRowCount(len(transactions))
        for row, trans in enumerate(transactions):
            self.inventory_transactions_table.setItem(row, 0, QTableWidgetItem(trans['type']))
            self.inventory_transactions_table.setItem(row, 1, QTableWidgetItem(str(trans['quantity'])))
            self.inventory_transactions_table.setItem(row, 2, QTableWidgetItem(str(trans['previous_quantity'] or '')))
            self.inventory_transactions_table.setItem(row, 3, QTableWidgetItem(str(trans['new_quantity'] or '')))
            self.inventory_transactions_table.setItem(row, 4, QTableWidgetItem(trans.get('reference', '')))
            self.inventory_transactions_table.setItem(row, 5, QTableWidgetItem(trans['created_at']))
        
        self.inventory_transactions_table.resizeColumnsToContents()
    
    def add_stock_action(self):
        """Add stock to product"""
        product_id = self.inventory_product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Please select a product!")
            return
        
        quantity = self.add_stock_qty.value()
        reference = self.inv_reference.text().strip()
        notes = self.inv_notes.toPlainText().strip()
        
        try:
            self.db.add_stock(product_id, quantity, reference, notes)
            QMessageBox.information(self, "Success", f"Added {quantity} units to stock!")
            self.load_inventory_product(product_id)
            self.refresh_all()
            
            # Clear fields
            self.inv_reference.clear()
            self.inv_notes.clear()
            self.add_stock_qty.setValue(10)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def remove_stock_action(self):
        """Remove stock from product"""
        product_id = self.inventory_product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Please select a product!")
            return
        
        quantity = self.remove_stock_qty.value()
        reference = self.inv_reference.text().strip()
        notes = self.inv_notes.toPlainText().strip()
        
        try:
            self.db.remove_stock(product_id, quantity, reference, notes)
            QMessageBox.information(self, "Success", f"Removed {quantity} units from stock!")
            self.load_inventory_product(product_id)
            self.refresh_all()
            
            # Clear fields
            self.inv_reference.clear()
            self.inv_notes.clear()
            self.remove_stock_qty.setValue(1)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def adjust_stock_action(self):
        """Adjust stock to specific quantity"""
        product_id = self.inventory_product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Please select a product!")
            return
        
        new_quantity = self.adjust_stock_qty.value()
        reference = self.inv_reference.text().strip()
        notes = self.inv_notes.toPlainText().strip()
        
        try:
            self.db.adjust_stock(product_id, new_quantity, reference, notes)
            QMessageBox.information(self, "Success", f"Stock adjusted to {new_quantity} units!")
            self.load_inventory_product(product_id)
            self.refresh_all()
            
            # Clear fields
            self.inv_reference.clear()
            self.inv_notes.clear()
            self.adjust_stock_qty.setValue(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    # ============ Image Functions ============
    
    def upload_image(self):
        """Upload product image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Product Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        
        if file_path:
            import uuid
            ext = os.path.splitext(file_path)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            target_path = os.path.join(self.images_dir, unique_name)
            
            try:
                shutil.copy2(file_path, target_path)
                self.image_path = target_path
                self.display_image(target_path)
                QMessageBox.information(self, "Success", "Image uploaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload image: {str(e)}")
    
    def remove_image(self):
        """Remove product image"""
        if self.image_path:
            try:
                if os.path.exists(self.image_path):
                    os.remove(self.image_path)
                self.image_path = None
                self.image_preview_label.setText("Product Image Preview")
                self.image_preview_label.setStyleSheet("")
                QMessageBox.information(self, "Success", "Image removed successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove image: {str(e)}")
    
    def display_image(self, image_path):
        """Display image in preview label"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_preview_label.width() - 20,
                    self.image_preview_label.height() - 20,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview_label.setPixmap(scaled_pixmap)
                self.image_preview_label.setScaledContents(False)
                self.image_preview_label.setStyleSheet("border: 2px solid #4CAF50;")
            else:
                self.image_preview_label.setText("Invalid Image")
                self.image_preview_label.setStyleSheet("")
    
    def display_image_in_table(self, image_path):
        """Get QTableWidgetItem with image for table"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(scaled_pixmap)
                item = QTableWidgetItem()
                item.setIcon(icon)
                return item
        return QTableWidgetItem("")
    
    def view_image(self, image_path):
        """View image in a separate dialog"""
        if image_path and os.path.exists(image_path):
            dialog = QDialog(self)
            dialog.setWindowTitle("Product Image")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            label = QLabel()
            pixmap = QPixmap(image_path)
            
            screen = QApplication.primaryScreen()
            size = screen.availableGeometry()
            max_size = min(size.width() * 0.8, size.height() * 0.8)
            
            if pixmap.width() > max_size or pixmap.height() > max_size:
                pixmap = pixmap.scaled(
                    int(max_size), int(max_size),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            
            scroll.setWidget(label)
            layout.addWidget(scroll)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn, alignment=Qt.AlignCenter)
            
            dialog.resize(int(max_size) + 50, int(max_size) + 100)
            dialog.exec_()
    
    # ============ Search ============
    
    def search_products(self, text):
        """Search products in real-time"""
        self.load_products()
    
    # ============ Dashboard Update ============
    
    def update_dashboard(self):
        """Update dashboard statistics and charts"""
        try:
            stats = self.db.get_statistics()
            
            # Update stats cards
            self.stats_cards['total_products'].setText(str(stats['total_products']))
            self.stats_cards['total_value'].setText(f"${stats['total_value']:,.2f}")
            self.stats_cards['low_stock'].setText(str(stats['low_stock']))
            self.stats_cards['out_of_stock'].setText(str(stats['out_of_stock']))
            self.stats_cards['total_suppliers'].setText(str(stats['total_suppliers']))
            self.stats_cards['recent_transactions'].setText(str(stats['recent_transactions']))
            
            # Update charts
            category_counts = self.db.get_category_counts()
            self.create_category_chart(category_counts)
            self.create_stock_chart(stats)
            
            # Recent transactions
            transactions = self.db.get_transactions(limit=20)
            self.recent_transactions_table.setRowCount(len(transactions))
            for row, trans in enumerate(transactions):
                self.recent_transactions_table.setItem(row, 0, QTableWidgetItem(trans.get('product_name', '')))
                self.recent_transactions_table.setItem(row, 1, QTableWidgetItem(trans['type']))
                self.recent_transactions_table.setItem(row, 2, QTableWidgetItem(str(trans['quantity'])))
                self.recent_transactions_table.setItem(row, 3, QTableWidgetItem(str(trans.get('previous_quantity', ''))))
                self.recent_transactions_table.setItem(row, 4, QTableWidgetItem(str(trans.get('new_quantity', ''))))
                self.recent_transactions_table.setItem(row, 5, QTableWidgetItem(trans['created_at'][:16]))
            
            self.recent_transactions_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def create_category_chart(self, data):
        """Create pie chart for category distribution"""
        try:
            series = QPieSeries()
            
            if data:
                total = sum(data.values())
                for category, count in data.items():
                    if count > 0:
                        percentage = (count / total) * 100
                        slice = series.append(f"{category}\n{count} ({percentage:.1f}%)", count)
                        slice.setLabelVisible(True)
                        slice.setLabelPosition(QPieSlice.LabelOutside)
            
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Products by Category")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setTheme(QChart.ChartThemeLight)
            chart.legend().setAlignment(Qt.AlignRight)
            chart.setBackgroundVisible(False)
            
            self.category_chart_view.setChart(chart)
        except Exception as e:
            print(f"Error creating category chart: {e}")
    
    def create_stock_chart(self, stats):
        """Create bar chart for stock status"""
        try:
            bar_set = QBarSet("Products")
            in_stock = max(0, stats['total_products'] - stats['low_stock'] - stats['out_of_stock'])
            bar_set.append([stats['out_of_stock'], stats['low_stock'], in_stock])
            
            series = QBarSeries()
            series.append(bar_set)
            
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Stock Status")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setTheme(QChart.ChartThemeLight)
            chart.setBackgroundVisible(False)
            
            categories = ["Out of Stock", "Low Stock", "In Stock"]
            axis = QBarCategoryAxis()
            axis.append(categories)
            chart.setAxisX(axis, series)
            
            self.stock_chart_view.setChart(chart)
        except Exception as e:
            print(f"Error creating stock chart: {e}")
    
    # ============ Transactions ============
    
    def load_transactions(self):
        """Load transaction history"""
        try:
            filter_text = self.transaction_product_filter.currentText()
            product_id = None
            if filter_text != "All Products":
                product_id = self.transaction_product_filter.currentData()
            
            trans_type = self.transaction_type_filter.currentText()
            
            transactions = self.db.get_inventory_transactions(product_id, limit=500)
            
            # Filter by type
            if trans_type != "All Types":
                transactions = [t for t in transactions if t['type'] == trans_type]
            
            self.transactions_table.setRowCount(len(transactions))
            
            for row, trans in enumerate(transactions):
                self.transactions_table.setItem(row, 0, QTableWidgetItem(trans.get('product_name', '')))
                self.transactions_table.setItem(row, 1, QTableWidgetItem(trans['type']))
                self.transactions_table.setItem(row, 2, QTableWidgetItem(str(trans['quantity'])))
                self.transactions_table.setItem(row, 3, QTableWidgetItem(str(trans.get('previous_quantity', ''))))
                self.transactions_table.setItem(row, 4, QTableWidgetItem(str(trans.get('new_quantity', ''))))
                self.transactions_table.setItem(row, 5, QTableWidgetItem(trans.get('reference', '')))
                self.transactions_table.setItem(row, 6, QTableWidgetItem(trans.get('created_by', '')))
                self.transactions_table.setItem(row, 7, QTableWidgetItem(trans['created_at'][:16]))
            
            self.transactions_table.resizeColumnsToContents()
            self.statusBar().showMessage(f"Loaded {len(transactions)} transactions", 2000)
        except Exception as e:
            print(f"Error loading transactions: {e}")
    
    # ============ Import Functions ============
    
    def choose_import_file(self):
        """Choose a file to import"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Import", "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.preview_import_file(file_path)
    
    def preview_import_file(self, file_path):
        """Preview the import file"""
        try:
            import pandas as pd
            
            # Read the file
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            if df.empty:
                QMessageBox.warning(self, "Warning", "The file is empty!")
                return
            
            # Show preview
            self.preview_table.setRowCount(min(20, len(df)))
            self.preview_table.setColumnCount(len(df.columns))
            self.preview_table.setHorizontalHeaderLabels(df.columns)
            
            for row in range(min(20, len(df))):
                for col in range(len(df.columns)):
                    value = df.iloc[row, col]
                    self.preview_table.setItem(row, col, QTableWidgetItem(str(value)))
            
            self.preview_table.resizeColumnsToContents()
            
            # Show stats
            required_cols = ['name', 'price', 'quantity']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            stats_text = f"📊 Total rows: {len(df)} | Columns: {len(df.columns)}"
            if missing_cols:
                stats_text += f" | ⚠️ Missing required columns: {', '.join(missing_cols)}"
                self.import_btn.setEnabled(False)
            else:
                stats_text += " | ✅ All required columns present!"
                self.import_btn.setEnabled(True)
            
            self.preview_stats_label.setText(stats_text)
            
            # Store the dataframe for import
            self.import_dataframe = df
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to preview file: {str(e)}")
            self.import_btn.setEnabled(False)
    
    def import_products(self):
        """Import products from the dataframe"""
        if not hasattr(self, 'import_dataframe') or self.import_dataframe is None:
            QMessageBox.warning(self, "Warning", "No data to import!")
            return
        
        df = self.import_dataframe
        
        # Confirm import
        reply = QMessageBox.question(
            self, "Confirm Import",
            f"Are you sure you want to import {len(df)} products?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Show progress bar
        self.import_progress.setVisible(True)
        self.import_progress.setRange(0, len(df))
        self.import_progress.setValue(0)
        
        # Import products
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Get or create supplier
                supplier_name = str(row.get('supplier', '')).strip()
                supplier_id = None
                if supplier_name:
                    supplier_id = self.db.get_supplier_id_by_name(supplier_name)
                    if not supplier_id:
                        supplier_id = self.db.add_supplier({'name': supplier_name})
                
                # Prepare data
                product_data = {
                    'name': str(row.get('name', '')).strip(),
                    'price': float(row.get('price', 0)),
                    'quantity': int(row.get('quantity', 0)),
                    'category': str(row.get('category', 'Other')).strip(),
                    'description': str(row.get('description', '')).strip(),
                    'supplier_id': supplier_id,
                    'min_quantity': int(row.get('min_quantity', 5)),
                    'barcode': str(row.get('barcode', '')).strip(),
                    'weight': float(row.get('weight', 0)),
                    'dimensions': str(row.get('dimensions', '')).strip(),
                    'notes': str(row.get('notes', '')).strip(),
                    'image_path': None
                }
                
                # Validate
                if not product_data['name']:
                    errors.append(f"Row {index + 2}: Missing name")
                    error_count += 1
                    continue
                
                if product_data['price'] <= 0:
                    errors.append(f"Row {index + 2}: Invalid price")
                    error_count += 1
                    continue
                
                # Add to database
                self.db.add_product(product_data)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                error_count += 1
            
            # Update progress
            self.import_progress.setValue(index + 1)
            QApplication.processEvents()
        
        # Hide progress bar
        self.import_progress.setVisible(False)
        
        # Show results
        result_msg = f"✅ Import completed!\n\n"
        result_msg += f"Successfully imported: {success_count} products\n"
        result_msg += f"Errors: {error_count}\n\n"
        
        if errors:
            result_msg += "Error details:\n"
            for error in errors[:10]:
                result_msg += f"• {error}\n"
            if len(errors) > 10:
                result_msg += f"• ... and {len(errors) - 10} more errors\n"
        
        QMessageBox.information(self, "Import Results", result_msg)
        
        # Refresh
        self.refresh_all()
        self.clear_import_preview()
    
    def clear_import_preview(self):
        """Clear the import preview"""
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.preview_stats_label.setText("No data loaded")
        self.file_path_label.setText("No file selected")
        self.import_btn.setEnabled(False)
        if hasattr(self, 'import_dataframe'):
            self.import_dataframe = None
    
    def download_template(self):
        """Download a template file"""
        try:
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Template", "product_template.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # Create template
            template_data = {
                'name': ['Sample Product 1', 'Sample Product 2'],
                'description': ['Description of product 1', 'Description of product 2'],
                'price': [19.99, 29.99],
                'quantity': [100, 50],
                'category': ['Electronics', 'Clothing'],
                'supplier': ['Supplier A', 'Supplier B'],
                'min_quantity': [5, 10],
                'barcode': ['123456789', '987654321'],
                'weight': [0.5, 1.2],
                'dimensions': ['10x5x3 cm', '20x15x10 cm'],
                'notes': ['Popular item', 'New collection']
            }
            
            df = pd.DataFrame(template_data)
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(
                self, "Success",
                f"Template downloaded successfully!\n\n"
                f"Location: {file_path}\n\n"
                f"Instructions:\n"
                f"1. Keep the column names (first row)\n"
                f"2. Add your product data below\n"
                f"3. Required columns: name, price, quantity\n"
                f"4. Save the file and import it back"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download template: {str(e)}")
    
    # ============ Reports ============
    
    def show_low_stock_report(self):
        """Show low stock report"""
        try:
            products = self.db.get_low_stock_products()
            
            report = "=== LOW STOCK REPORT ===\n\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"Total low stock items: {len(products)}\n\n"
            
            if products:
                report += "ID\tName\t\t\tQuantity\tMin Qty\tSupplier\n"
                report += "-" * 70 + "\n"
                for p in products:
                    name = p['name'][:20].ljust(20)
                    report += f"{p['id']}\t{name}\t{p['quantity']}\t\t{p['min_quantity']}\t{p.get('supplier_name', 'N/A')}\n"
            else:
                report += "✅ No low stock items found!\n"
            
            self.report_display.setText(report)
            self.switch_to_tab(7)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def show_value_report(self):
        """Show inventory value report"""
        try:
            products = self.db.get_all_products()
            categories = self.db.get_category_counts()
            
            report = "=== INVENTORY VALUE REPORT ===\n\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Summary
            total_value = sum(p['price'] * p['quantity'] for p in products)
            total_quantity = sum(p['quantity'] for p in products)
            
            report += f"Total Products: {len(products)}\n"
            report += f"Total Quantity: {total_quantity}\n"
            report += f"Total Value: ${total_value:,.2f}\n"
            report += f"Average Price: ${(total_value/len(products)) if products else 0:,.2f}\n\n"
            
            # By category
            report += "=== BY CATEGORY ===\n"
            report += "Category\t\tCount\tValue\n"
            report += "-" * 40 + "\n"
            
            for category, count in categories.items():
                cat_products = [p for p in products if p['category'] == category]
                cat_value = sum(p['price'] * p['quantity'] for p in cat_products)
                report += f"{category[:15]}\t\t{count}\t${cat_value:,.2f}\n"
            
            # Top products by value
            report += "\n=== TOP 10 PRODUCTS BY VALUE ===\n"
            sorted_products = sorted(products, key=lambda p: p['price'] * p['quantity'], reverse=True)[:10]
            
            for i, p in enumerate(sorted_products, 1):
                value = p['price'] * p['quantity']
                report += f"{i}. {p['name'][:20]} - ${value:,.2f} ({p['quantity']} @ ${p['price']:.2f})\n"
            
            self.report_display.setText(report)
            self.switch_to_tab(7)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def show_supplier_report(self):
        """Show supplier report"""
        try:
            suppliers = self.db.get_all_suppliers()
            
            report = "=== SUPPLIER REPORT ===\n\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"Total Suppliers: {len(suppliers)}\n\n"
            
            if suppliers:
                report += "Name\t\t\tProducts\tContact\t\tPhone\n"
                report += "-" * 70 + "\n"
                for s in suppliers:
                    name = s['name'][:20].ljust(20)
                    contact = s.get('contact_person', 'N/A')[:15].ljust(15)
                    phone = s.get('phone', 'N/A')[:12].ljust(12)
                    report += f"{name}\t{s.get('product_count', 0)}\t\t{contact}\t{phone}\n"
            else:
                report += "No suppliers found!\n"
            
            self.report_display.setText(report)
            self.switch_to_tab(7)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def export_csv(self):
        """Export products to CSV file"""
        try:
            import csv
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Products", "", "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
            
            products = self.db.get_all_products(include_inactive=True)
            
            if not products:
                QMessageBox.warning(self, "Warning", "No products to export!")
                return
            
            # Get all fields
            fields = list(products[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(products)
            
            QMessageBox.information(self, "Success", f"Exported {len(products)} products to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    # ============ Utility Functions ============
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Product Management System",
            """
            <h1>Product Management System</h1>
            <p>Version 3.0</p>
            <p>A comprehensive desktop application for managing products, 
            inventory, and suppliers.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Product CRUD with image support</li>
                <li>Supplier management</li>
                <li>Inventory operations (add/remove/adjust)</li>
                <li>Barcode lookup</li>
                <li>Bulk import from Excel/CSV</li>
                <li>Export to CSV</li>
                <li>Real-time search and filtering</li>
                <li>Transaction history with audit trail</li>
                <li>Dashboard with statistics and charts</li>
                <li>Low stock alerts</li>
                <li>Active/inactive product toggling</li>
                <li>Supplier directory with product counts</li>
                <li>Comprehensive reporting</li>
                <li>SQLite local database</li>
            </ul>
            <p>Built with Python, PyQt5, Pandas, and SQLite</p>
            <p>© 2024 Product Management System</p>
            """
        )
    
    def switch_to_tab(self, index):
        """Switch to a specific tab"""
        self.centralWidget().setCurrentIndex(index)
    
    def resizeEvent(self, event):
        """Handle window resize for image preview"""
        super().resizeEvent(event)
        if hasattr(self, 'image_path') and self.image_path:
            self.display_image(self.image_path)
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self, "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ProductManagementApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()