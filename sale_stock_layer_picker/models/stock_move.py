# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.tools import float_round

class StockMove(models.Model):
    _inherit = 'stock.move'

    target_layer_id = fields.Many2one('stock.valuation.layer', string="Target Cost Layer")
    unit_cost = fields.Float(related='target_layer_id.unit_cost', string="Target Cost", readonly=True)

    def _create_out_svl(self, forced_quantity=None):
        svl_all = self.env['stock.valuation.layer']
        
        moves_with_target = self.filtered(lambda m: m.target_layer_id)
        for move in moves_with_target:
            svl_all |= move._process_custom_fifo(forced_quantity)

        moves_standard = self - moves_with_target
        for move in moves_standard:
            if move.product_id.cost_method == 'fifo':
                svl_all |= move._process_standard_fifo(forced_quantity)
            else:
                svl_all |= super(StockMove, move)._create_out_svl(forced_quantity=forced_quantity)

        return svl_all

    def _process_custom_fifo(self, forced_quantity=None):
        self.ensure_one()
        quantity = abs(forced_quantity or self.product_qty)
        
        layer = self.target_layer_id
        if layer.remaining_qty:
            unit_cost = layer.remaining_value / layer.remaining_qty
        else:
            unit_cost = layer.unit_cost

        value = unit_cost * quantity
        value = float_round(value, precision_rounding=self.company_id.currency_id.rounding)

        self.target_layer_id.sudo().write({
            'remaining_qty': self.target_layer_id.remaining_qty - quantity,
            'remaining_value': self.target_layer_id.remaining_value - value
        })

        return self._create_svl_record(quantity, unit_cost, value, self.target_layer_id.id)

    def _process_standard_fifo(self, forced_quantity=None):
        self.ensure_one()
        qty_to_take = abs(forced_quantity or self.product_qty)
        svls = self.env['stock.valuation.layer']

        candidates = self.env['stock.valuation.layer'].search([
            ('product_id', '=', self.product_id.id),
            ('remaining_qty', '>', 0),
            ('company_id', '=', self.company_id.id),
        ], order='create_date, id')

        for cand in candidates:
            if qty_to_take <= 0:
                break
            
            qty_taken = min(qty_to_take, cand.remaining_qty)
            qty_to_take -= qty_taken

            if cand.remaining_qty:
                unit_cost = cand.remaining_value / cand.remaining_qty
            else:
                unit_cost = cand.unit_cost

            value = unit_cost * qty_taken
            value = float_round(value, precision_rounding=self.company_id.currency_id.rounding)

            cand.sudo().write({
                'remaining_qty': cand.remaining_qty - qty_taken,
                'remaining_value': cand.remaining_value - value
            })
            
            svls |= self._create_svl_record(qty_taken, unit_cost, value, cand.id)

        if qty_to_take > 0:
            unit_cost = self.product_id.standard_price
            value = unit_cost * qty_to_take
            svls |= self._create_svl_record(qty_to_take, unit_cost, value, False)
            
        return svls

    def _create_svl_record(self, quantity, unit_cost, value, layer_id):
        svl_vals = {
            'stock_move_id': self.id,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'quantity': -quantity,
            'unit_cost': unit_cost,
            'value': -value,
            'remaining_qty': 0,
            'remaining_value': 0,
            'description': self.reference,
            'stock_valuation_layer_id': layer_id,
        }
        return self.env['stock.valuation.layer'].sudo().create(svl_vals)