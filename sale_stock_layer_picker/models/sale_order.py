# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if self.env.context.get('skip_layer_check'):
            return super(SaleOrder, self).action_confirm()

        lines_without_layer = self.order_line.filtered(
            lambda l: not l.display_type and 
                      not l.target_layer_id and 
                      l.product_id.type == 'product'
        )

        if lines_without_layer:
            product_names = ", ".join(lines_without_layer.mapped('product_id.name')[:3])
            if len(lines_without_layer) > 3:
                product_names += " ...وغيرهم"

            msg = (
                f"يا صديقي، شكلك نسيت تختار الدفعة (Batch) للمنتجات دي:\n"
                f"[ {product_names} ]\n\n"
                f"هل أنت متأكد إنك عايز تبيع 'عالعمياني' بنظام FIFO وتضيع علينا فرصة اختيار التكلفة؟ 🤔"
            )

            return {
                'name': 'لحظة من فضلك!',
                'type': 'ir.actions.act_window',
                'res_model': 'sales.confirm.warning.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_message': msg, 'default_sale_order_id': self.id}
            }

        return super(SaleOrder, self).action_confirm()

    def get_merged_lines_for_print(self):
        grouped_data = {}
        for line in self.order_line.filtered(lambda l: not l.display_type):
            key = (line.product_id, line.price_unit, line.name, line.product_uom)
            if key in grouped_data:
                grouped_data[key]['product_uom_qty'] += line.product_uom_qty
                grouped_data[key]['price_subtotal'] += line.price_subtotal
            else:
                grouped_data[key] = {
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'currency_id': self.currency_id,
                    'tax_id': line.tax_id,
                    'discount': line.discount,
                }
        return list(grouped_data.values())

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    target_layer_id = fields.Many2one(
        'stock.valuation.layer', 
        string="Target Cost Batch", 
        copy=False
    )

    def action_open_layer_picker(self):
        self.ensure_one()
        return {
            'name': 'Pick Inventory Batch',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.layer.picker',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_line_id': self.id}
        }

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        if self.target_layer_id:
            values['target_layer_id'] = self.target_layer_id.id
        return values