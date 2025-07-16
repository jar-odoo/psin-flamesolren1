from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    master_price = fields.Float(string='Master Price', store=True)
    last_price = fields.Float(string='Last Purchase Price', store=True)
