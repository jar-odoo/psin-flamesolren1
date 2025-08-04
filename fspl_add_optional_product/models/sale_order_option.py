from odoo import models, fields


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    is_selected = fields.Boolean(string="Select")

    def _get_values_to_add_to_order(self):
        result = super()._get_values_to_add_to_order()
        result.update({'price_unit': 0.00, 'product_uom_qty': self.required_qty})
        return result
