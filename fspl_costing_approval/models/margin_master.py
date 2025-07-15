from odoo import fields, models


class MarginMaster(models.Model):
    _name = "margin.master"
    _description = "Margin Master"

    name = fields.Char(string="Name")
    margin_per_kw = fields.Float(string="Margin / KW")
    user_ids = fields.Many2many("res.users", string="Users")
    city_id = fields.Many2one("res.city", string="City")
