from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    select_all_options = fields.Boolean(string="Select All Optional Products")
    all_options_added_to_sale_order = fields.Boolean(
        string="All Optional Products Added",
        compute="_compute_all_options_added_to_sale_order"
    )

    @api.depends('sale_order_option_ids.is_present')
    def _compute_all_options_added_to_sale_order(self):
        for order in self:
            options = order.sale_order_option_ids
            order.all_options_added_to_sale_order = all(option.is_present for option in options)

    def action_add_selected_options_to_order(self):
        selected_options = self.sale_order_option_ids.filtered(lambda opt: opt.is_selected)
        for option in selected_options:
            option.button_add_to_order()
            option.is_selected =False
        self.select_all_options = False

    @api.onchange('select_all_options')
    def _onchange_select_all_options(self):
        for line in self.sale_order_option_ids:
            line.is_selected = self.select_all_options
