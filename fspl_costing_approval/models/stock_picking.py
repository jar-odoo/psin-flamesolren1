from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_last_purchase_price = fields.Boolean(related='picking_type_id.is_last_purchase_price')
    is_total_amount = fields.Boolean(related='picking_type_id.is_total_amount')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for move in self.move_ids:
            move._get_last_purchase_price_and_total_amount()
        return res
