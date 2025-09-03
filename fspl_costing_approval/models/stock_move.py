from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    last_purchase_price = fields.Float(string='Last Purchase Price', readonly=True, store=True)
    total_amount = fields.Float(string='Total Amount', store=True, readonly=True)

    def _get_last_purchase_price_and_total_amount(self):
        for move in self:
            if move.picking_id and move.picking_id.is_last_purchase_price:
                move.last_purchase_price = move.product_id.last_price
            if move.picking_id and move.picking_id.is_total_amount:
                move.total_amount = move.last_purchase_price * move.quantity
