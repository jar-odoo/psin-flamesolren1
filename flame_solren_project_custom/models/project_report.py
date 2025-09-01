# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"
    
    creation_plan = fields.Boolean(string="Creation Plan", readonly=True)
    no_of_days = fields.Integer(string="No. of Days", help='The number of days estimated or planned for the task', readonly=True)
    planned_scheduled_start_date = fields.Date(string="Planned Scheduled Start Date", readonly=True)
    planned_scheduled_end_date = fields.Date(string="Planned Scheduled End Date", readonly=True)
    actual_start_date = fields.Date(string="Actual Start Date", readonly=True)
    actual_end_date = fields.Date(string="Actual End Date", readonly=True)
    state = fields.Selection(
        selection_add=[('05_to_do', 'To-Do')],
    )
    
    def _select(self):
        return super()._select() +  """,
                t.creation_plan,
                t.no_of_days,
                t.planned_scheduled_start_date,
                t.planned_scheduled_end_date,
                t.actual_start_date,
                t.actual_end_date
        """
    
    def _group_by(self):
        return super()._group_by() + """,
                t.creation_plan,
                t.no_of_days,
                t.planned_scheduled_start_date,
                t.planned_scheduled_end_date,
                t.actual_start_date,
                t.actual_end_date
        """
