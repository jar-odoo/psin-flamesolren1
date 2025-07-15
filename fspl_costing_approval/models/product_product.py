from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    master_price = fields.Float(string='Master Price', store=True)
    last_price = fields.Float(string='Last Purchase Price', store=True)


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
