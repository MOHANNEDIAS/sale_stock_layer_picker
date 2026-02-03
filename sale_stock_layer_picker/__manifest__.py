# -*- coding: utf-8 -*-
{
    'name': "Sale Stock Layer Picker",
    'summary': "Select specific cost layers (batches) directly from Sales Order",
    'description': """
        Allows salespersons to pick specific cost layers (valuation layers) 
        to sell from, ensuring accurate profit margin calculation without using lots.
        
        Features:
        - Wizard to split sales lines across multiple cost layers.
        - Enforces FIFO override in Stock Moves based on selection.
        - Merges split lines in PDF Reports for cleaner customer view (SO & Invoice).
    """,
    'author': "MO",
    'category': 'Sales/Inventory',
    'version': '18.0.1.0.0',
    'depends': ['sale_management', 'stock_account', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_layer_picker_view.xml',
        'wizard/confirm_warning_view.xml',
        'views/sale_order_view.xml',
        'views/report_saleorder.xml',
        'views/report_invoice.xml',
        'views/stock_picking_view.xml',
    ],
    'application': True,
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'price': 10.00,
    'currency': 'EUR',
    'license': 'OPL-1',
}