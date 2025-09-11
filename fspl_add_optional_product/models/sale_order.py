# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    select_all_options = fields.Boolean(string="Select All Optional Products")

    def action_add_selected_options_to_order(self):
        # Filter remove all option line which is present in order line.
        selected_options = self.sale_order_option_ids.filtered(lambda opt: opt.is_selected and not opt.is_present)
        for option in selected_options:
            option.with_context(fspl_add_options=True).button_add_to_order()
        self.select_all_options = False

    @api.onchange('select_all_options')
    def _onchange_select_all_options(self):
        for line in self.sale_order_option_ids:
            line.is_selected = self.select_all_options

    def action_confirm(self):
        for order in self:
            for option in order.sale_order_option_ids:
                option.write({'project_coordinator_qty': option.required_qty})
        return super().action_confirm()
