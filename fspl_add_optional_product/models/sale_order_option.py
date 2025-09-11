# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    is_selected = fields.Boolean(string="Select")
    project_coordinator_qty = fields.Float(
        string="Project Co-ordinator Qty",
        help="Defaults to Required Qty but can be adjusted manually by user."
    )

    def _get_values_to_add_to_order(self):
        result = super()._get_values_to_add_to_order()
        result.update({'price_unit': 0.00, 'product_uom_qty': self.project_coordinator_qty})
        return result

    def _can_be_edited_on_portal(self):
        self.ensure_one()
        if self._context.get('fspl_add_options', False):
            return True
        return super()._can_be_edited_on_portal()
