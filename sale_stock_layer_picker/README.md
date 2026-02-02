# Sale Stock Layer Picker for Odoo 18

## Overview
This module solves the specific identification costing problem without enforcing serial numbers usage. It allows salespersons to manually select which inventory cost layer (batch) to sell from directly in the Sales Order.

## Key Features
1.  **Cost Selector Wizard:** A popup in Sales Order Lines to view available inventory batches with their specific costs.
2.  **Split Line Logic:** Automatically splits the sales line into multiple lines if quantities are picked from different cost layers.
3.  **Smart Delivery:** Overrides standard FIFO logic to force the warehouse to consume the specifically selected layer.
4.  **Clean Reporting:** Merges split lines in the PDF Quotation/Order so the customer sees a single line item.

## How to Use
1.  Create a Quotation.
2.  Add a product (e.g., iPhone).
3.  Click the **List Icon** button next to the quantity field.
4.  Enter the quantity you want to take from each available batch.
5.  Click **Apply**.
6.  Confirm the order. The system will handle the costing automatically.