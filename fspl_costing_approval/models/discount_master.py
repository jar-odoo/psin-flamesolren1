from odoo import fields, models


class DiscountMaster(models.Model):
    _name = "discount.master"
    _description = "Discount Master"

    name = fields.Char(string="Name", required=True)
    discount_per_kw = fields.Float(string="Discount / KW")
    city_id = fields.Many2one("res.city", string="City")
    user_ids = fields.Many2many("res.users", string="Users")
    approval_category_id = fields.Many2one('approval.category', string="Approval Category")
