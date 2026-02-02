# -*- coding: utf-8 -*-
from odoo import models, fields

class SalesConfirmWarningWizard(models.TransientModel):
    _name = 'sales.confirm.warning.wizard'
    _description = 'Sales Confirmation Warning'

    message = fields.Text(string="Message", readonly=True)
    sale_order_id = fields.Many2one('sale.order', string="Sales Order")

    def action_confirm_anyway(self):
        self.ensure_one()
        return self.sale_order_id.with_context(skip_layer_check=True).action_confirm()