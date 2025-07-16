from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            for line in order.order_line:
                product = line.product_id
                if product:
                    product.last_price = line.price_unit
        return res
