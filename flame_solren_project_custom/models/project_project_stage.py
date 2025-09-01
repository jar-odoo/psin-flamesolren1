# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'
    
    is_cancelled_stage = fields.Boolean(string="Is Cancelled Stage")
