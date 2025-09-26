# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            tasks = self.env['project.task'].search([
                ('sale_line_id', 'in', order.order_line.ids),
            ])
            if tasks:
                tasks._schedule_tasks_finish_to_start(order.date_order)
                for task in tasks:
                    if not task.depend_on_ids:
                        task.state = '05_to_do'
                        task.actual_start_date = False
                        task.actual_end_date = False
        return res
    
    def _action_cancel(self):
        res = super()._action_cancel()
        cancel_stage = self.env['project.project.stage'].search([('is_cancelled_stage', '=', True)], limit=1)
        if cancel_stage:
            self.project_ids.write({'stage_id': cancel_stage.id})
        self.tasks_ids.filtered(lambda t: t.state not in ['1_done', '1_canceled']).write({'state': '1_canceled'})
        return res
