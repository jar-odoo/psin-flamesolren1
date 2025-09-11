from odoo import fields, models


class SaleOrderTemplateOption(models.Model):
    _inherit = 'sale.order.template.option'

    def _prepare_option_line_values(self):
        """ Paased quantity's value to required quantity for better comparision."""
        self.ensure_one()
        res = super()._prepare_option_line_values()
        res['required_qty'] = self.quantity
        return res
