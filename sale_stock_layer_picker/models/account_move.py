# -*- coding: utf-8 -*-
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_merged_invoice_lines_for_print(self):
        grouped_lines = {}
        # تصحيح الفلتر: نقبل السطور التي نوعها 'product' أو الفارغة (للاحتياط)
        # ونستبعد فقط العناوين (line_section) والملاحظات (line_note)
        valid_types = ['product', False] 
        
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type in valid_types):
            key = (line.product_id, line.price_unit, line.name, line.product_uom_id)
            
            if key in grouped_lines:
                grouped_lines[key]['quantity'] += line.quantity
                grouped_lines[key]['price_subtotal'] += line.price_subtotal
            else:
                grouped_lines[key] = {
                    'product_id': line.product_id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'product_uom_id': line.product_uom_id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'currency_id': self.currency_id,
                    'tax_ids': line.tax_ids,
                    'discount': line.discount,
                }
        return list(grouped_lines.values())