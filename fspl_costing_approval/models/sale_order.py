from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dc_capacity_kwp = fields.Float(string="DC Capacity (KWp)", tracking=True, copy=False, store=True)
    base_amount_per_kw = fields.Float(string="Base Amount per KW", compute="_compute_base_amount", store=True, copy=False)
    material_cost = fields.Float(string="Material Cost", store=True, compute="_compute_costs", copy=False)
    expense_cost = fields.Float(string="Expense Cost", store=True, compute="_compute_costs", copy=False)
    discount_amount = fields.Float(string="Discount", tracking=True, copy=False, store=True)
    margin_with_dc = fields.Float(string="Margin with DC", copy=False, compute='_calculate_margin_with_dc_capacity', store=True)
    discount_with_dc = fields.Float(string="Discount with DC", copy=False)
    final_sales_kwp_without_tax = fields.Float(string="Final Amount /kwp Untaxed", copy=False, compute='_compute_base_amount', store=True)
    final_amt_without_tax = fields.Float(string="Final Amount Untaxed", copy=False, compute='_compute_base_amount', store=True)
    approval_requested = fields.Boolean(string="Approval Requested", copy=False, readonly=True)
    sales_70 = fields.Float(string="70% Amount", readonly=True, copy=False, compute='_compute_final_amt_without_tax', store=True)
    sales_30 = fields.Float(string="30% Amount", readonly=True, copy=False, compute='_compute_final_amt_without_tax', store=True)
    option_tax_totals = fields.Binary(compute='_compute_option_tax_totals_json', exportable=False)
    approval_request_id = fields.Many2one('approval.request', string='Discount Approval Request', readonly=True, copy=False)
    discount_tooltip = fields.Char(readonly=True)


    def action_open_discount_approval(self):
        self.ensure_one()
        if self.approval_request_id:
            return {
                'name': 'Discount Approval',
                'type': 'ir.actions.act_window',
                'res_model': 'approval.request',
                'res_id': self.approval_request_id.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_sale_order_id': self.id},
            }

    @api.depends('dc_capacity_kwp', 'sale_order_option_ids', 'margin_with_dc', 'discount_with_dc', 'final_sales_kwp_without_tax')
    def _compute_base_amount(self):
        for order in self:
            if order.dc_capacity_kwp > 0:
                optional_products_untaxed_amt = sum(order.sale_order_option_ids.mapped('final_amount'))
                margin_per_kw = order.margin_with_dc / order.dc_capacity_kwp if order.dc_capacity_kwp > 0 else 0
                order.base_amount_per_kw = optional_products_untaxed_amt / order.dc_capacity_kwp
                order.final_sales_kwp_without_tax = order.base_amount_per_kw + margin_per_kw
                order.final_amt_without_tax = (order.final_sales_kwp_without_tax * order.dc_capacity_kwp) - order.discount_with_dc

    @api.depends('sale_order_option_ids')
    def _compute_costs(self):
        for order in self:
            material_total = 0.0
            expense_total = 0.0
            for line in order.sale_order_option_ids:
                if line.product_id.is_storable:
                    material_total += line.final_amount
                else:
                    expense_total += line.final_amount
            order.material_cost = material_total
            order.expense_cost = expense_total

    @api.depends('final_amt_without_tax', 'dc_capacity_kwp')
    def _compute_final_amt_without_tax(self):
        for order in self:
            if order.dc_capacity_kwp > 0:
                order.sales_70 = (order.final_amt_without_tax * 0.70) / order.dc_capacity_kwp
                order.sales_30 = (order.final_amt_without_tax * 0.30) / order.dc_capacity_kwp

    @api.depends_context('lang')
    @api.depends('sale_order_option_ids.final_amount', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_option_tax_totals_json(self):
        AccountTax = self.env['account.tax']
        for order in self:
            option_lines = order.sale_order_option_ids
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in option_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.option_tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

    @api.depends('dc_capacity_kwp')
    def _calculate_margin_with_dc_capacity(self):
        for order in self:
            margin_master = self.env['margin.master'].search([('user_ids', 'in', self.env.user.id), '|', ('city_id', '=', order.partner_id.city_id.id), ('city_id.name', '=', order.partner_id.city)], limit=1)
            if margin_master and order.dc_capacity_kwp:
                per_kw_margin = margin_master.margin_per_kw * order.dc_capacity_kwp
                order.margin_with_dc = per_kw_margin
            else:
                order.margin_with_dc = 0.0

    def action_send_for_approval(self):
        for order in self:
            per_kw_discount = order.discount_amount * order.dc_capacity_kwp
            discount_master = self.env['discount.master'].search([
                ('user_ids', 'in', self.env.user.id),
                '|',
                ('city_id', '=', order.partner_id.city_id.id),
                ('city_id.name', '=', order.partner_id.city)
            ], limit=1)
            approval = self.env['approval.request'].create({
                'name': f"Discount Approval for {order.name}",
                'request_owner_id': self.env.user.id,
                'category_id': discount_master.approval_category_id.id,
                'sale_order_id': order._origin.id,
                'reason': f"Discount of ₹{order.discount_amount} exceeds allowed per-kW for {order.dc_capacity_kwp} kW",
            })
            order._origin.write({
                'approval_request_id': approval.id,
                'approval_requested': True
                })
            order.action_lock()

    @api.onchange('discount_amount', 'dc_capacity_kwp')
    def action_check_discount(self):
        for order in self:
            discount_master = self.env['discount.master'].search([
                ('user_ids', 'in', self.env.user.id),
                '|',
                ('city_id', '=', order.partner_id.city_id.id),
                ('city_id.name', '=', order.partner_id.city)
            ], limit=1)
            if not discount_master:
                continue
            if discount_master and order.discount_amount > discount_master.discount_per_kw:
                order.discount_tooltip = f"Discount amount has been exceeded. You can not apply discount more than { discount_master.discount_per_kw * order.dc_capacity_kwp }."
            else:
                order.discount_tooltip = False
                order.discount_with_dc = order.discount_amount * order.dc_capacity_kwp
