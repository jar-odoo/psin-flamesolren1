from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_last_purchase_price = fields.Boolean('Last Purchase Price')
    is_total_amount = fields.Boolean('Total Amount')
