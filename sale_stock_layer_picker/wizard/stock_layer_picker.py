# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockLayerPicker(models.TransientModel):
    _name = 'stock.layer.picker'
    _description = 'Pick Cost Layers for Sales'

    sale_line_id = fields.Many2one('sale.order.line', required=True)
    product_id = fields.Many2one('product.product', related='sale_line_id.product_id')
    company_id = fields.Many2one('res.company', related='sale_line_id.company_id')
    line_ids = fields.One2many('stock.layer.picker.line', 'wizard_id', string="Available Batches")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_sale_line_id'):
            line = self.env['sale.order.line'].browse(self.env.context.get('default_sale_line_id'))
            
            domain = [
                ('product_id', '=', line.product_id.id),
                ('remaining_qty', '>', 0),
                ('company_id', '=', line.company_id.id)
            ]
            layers = self.env['stock.valuation.layer'].search(domain, order='create_date asc')
            
            lines_data = []
            for layer in layers:
                if layer.remaining_qty:
                    real_cost = layer.remaining_value / layer.remaining_qty
                else:
                    real_cost = layer.unit_cost

                lines_data.append((0, 0, {
                    'layer_id': layer.id,
                    'unit_cost': real_cost,
                    'available_qty': layer.remaining_qty,
                    'create_date': layer.create_date,
                }))
            res['line_ids'] = lines_data
        return res

    def action_apply(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered(lambda l: l.selected_qty > 0)
        
        if not selected_lines:
            raise UserError(_("Please enter a quantity for at least one batch."))

        sale_line = self.sale_line_id
        order = sale_line.order_id
        
        first_selection = selected_lines[0]
        
        sale_line.write({
            'product_uom_qty': first_selection.selected_qty,
            'target_layer_id': first_selection.layer_id.id
        })
        
        for selection in selected_lines[1:]:
            sale_line.copy({
                'order_id': order.id,
                'product_uom_qty': selection.selected_qty,
                'target_layer_id': selection.layer_id.id
            })
            
        return {'type': 'ir.actions.act_window_close'}

class StockLayerPickerLine(models.TransientModel):
    _name = 'stock.layer.picker.line'
    _order = 'create_date asc'

    wizard_id = fields.Many2one('stock.layer.picker')
    layer_id = fields.Many2one('stock.valuation.layer', required=True)
    create_date = fields.Datetime(string="Date In", readonly=True)
    unit_cost = fields.Float(string="Cost", readonly=True)
    available_qty = fields.Float(string="Available", readonly=True)
    selected_qty = fields.Float(string="Pick Qty")

    @api.onchange('selected_qty')
    def _check_max_qty(self):
        if self.selected_qty > self.available_qty:
            self.selected_qty = self.available_qty
            return {'warning': {
                'title': _('Quantity Limit'), 
                'message': _('You cannot pick more than available in this batch.')
            }}