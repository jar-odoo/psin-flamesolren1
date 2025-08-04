from odoo import models, fields


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    is_selected = fields.Boolean(string="Select")

    def button_add_to_order(self):
        existing_products = self.order_id.order_line.mapped('product_id')

        if self.product_id in existing_products:
            return
        result = self.add_option_to_order()
        self.is_selected =False
        result.write({
            'product_uom_qty': self.required_qty,
            'price_unit': 0.00,
            'tax_id': False,
        })
