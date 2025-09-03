# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    select_all_options = fields.Boolean(string="Select All Optional Products")

    def action_add_selected_options_to_order(self):
        # Filter remove all option line which is present in order line.
        selected_options = self.sale_order_option_ids.filtered(lambda opt: opt.is_selected and not opt.is_present)
        for option in selected_options:
            option.button_add_to_order()
        self.select_all_options = False

    @api.onchange('select_all_options')
    def _onchange_select_all_options(self):
        for line in self.sale_order_option_ids:
            line.is_selected = self.select_all_options
