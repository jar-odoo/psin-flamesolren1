from collections import defaultdict

from odoo import models, fields, api


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    required_qty = fields.Float(string="Required Qty", default=1.0)
    standard_cost_price = fields.Float(string="Cost", readonly=True, related='product_id.standard_price')
    last_previous_price = fields.Float(string="Last Price", readonly=True, related='product_id.last_price')
    tax_id = fields.Many2many(comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False,
        context={'active_test': False},
        check_company=True)
    final_amount = fields.Float(string="Final Amount", compute="_compute_final_amount", store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related="order_id.company_id")


    @api.depends('product_id', 'uom_id', 'quantity')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for option in self:
            option.price_unit = option.product_id.master_price

    @api.depends('required_qty', 'price_unit')
    def _compute_final_amount(self):
        for line in self:
            line.final_amount = line.required_qty * line.price_unit

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            **{
                'tax_ids': self.tax_id,
                'quantity': self.required_qty,
                'partner_id': self.order_id.partner_id,
                'currency_id': self.order_id.currency_id or self.order_id.company_id.currency_id,
                'rate': self.order_id.currency_rate,
                **kwargs,
            },
        )

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        lines_by_company = defaultdict(lambda: self.env['sale.order.option'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                if not line.product_id or not taxes:
                    line.tax_id = False
                    continue
                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                line.tax_id = result
