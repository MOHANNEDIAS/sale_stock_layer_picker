# -*- coding: utf-8 -*-
from odoo import models

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        
        if values.get('target_layer_id'):
            res['target_layer_id'] = values['target_layer_id']
            
        return res