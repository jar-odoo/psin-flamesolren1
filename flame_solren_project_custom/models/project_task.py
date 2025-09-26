# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from datetime import date, timedelta
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    no_of_days = fields.Integer(string="No. of Days", help='The number of days estimated or planned for the task', tracking=True)
    planned_scheduled_start_date = fields.Date(string="Planned Scheduled Start Date", compute="_compute_planned_scheduled_start_date", store=True , tracking=True)
    planned_scheduled_end_date = fields.Date(string="Planned Scheduled End Date", compute="_compute_planned_scheduled_end_date", store=True, tracking=True)
    creation_plan = fields.Boolean(string="Creation Plan", tracking=True)
    actual_start_date = fields.Date(string="Actual Start Date", tracking=True)
    actual_end_date = fields.Date(string="Actual End Date", tracking=True)
    state = fields.Selection(
        selection_add=[('05_to_do', 'To-Do')],
        ondelete={'05_to_do': 'set default'},
    default='05_to_do'
    )
    delay_early_planned = fields.Integer(string="Delay/Early Based On Planned", compute="_compute_delay_early_planned")
    delay_early_actual = fields.Integer(string="Delay/Early Based On Actual", compute="_compute_delay_early_actual")  
    
    _sql_constraints = [
        ('planned_scheduled_dates_check', "CHECK ((planned_scheduled_start_date <= planned_scheduled_end_date))", "The planned scheduled start date must be before the planned scheduled end date."),
    ]
    
    def _compute_delay_task(self, start_date=False, end_date=False):
        delay = 0
        if start_date and end_date:
            delay = (start_date - end_date.date()).days
        return delay
    
    @api.depends('planned_scheduled_end_date', 'date_deadline')
    def _compute_delay_early_planned(self):
        for task in self:
            task.delay_early_planned = task._compute_delay_task(task.planned_scheduled_end_date, task.date_deadline)
            
    @api.depends('actual_end_date', 'date_deadline')
    def _compute_delay_early_actual(self):
        for task in self:
            task.delay_early_actual = task._compute_delay_task(task.actual_end_date, task.date_deadline)
    
    @api.depends('sale_line_id', 'creation_plan')
    def _compute_planned_scheduled_start_date(self):
        for task in self:
            if task.sale_line_id and task.sale_line_id.order_id.date_order and task.creation_plan:
                task.planned_scheduled_start_date = task.sale_line_id.order_id.date_order.date() + timedelta(days=1)
                
    @api.depends('no_of_days')
    def _compute_planned_scheduled_end_date(self):
        for task in self:
            if task.planned_scheduled_start_date:
                task.planned_scheduled_end_date = task.planned_scheduled_start_date + timedelta(days=task.no_of_days)
            else:
                task.planned_scheduled_end_date = False
                
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.state != '04_waiting_normal':
            self.state = '05_to_do'
    
    def _schedule_tasks_finish_to_start(self, base_date):
        sale_date = base_date.date() + timedelta(days=1)
        date_map = {}
        def get_tasks_in_dependency_order(tasks):
            visited = set()
            result = []
            def visit(task):
                if task.id in visited:
                    return
                for dep in task.depend_on_ids:
                    visit(dep)
                visited.add(task.id)
                result.append(task)
            for task in tasks:
                visit(task)
            return result
        all_tasks = self | self.mapped('dependent_ids')
        sorted_tasks = get_tasks_in_dependency_order(all_tasks)
        for task in sorted_tasks:
            if task.creation_plan:
                continue
            latest_end = sale_date - timedelta(days=1)
            for dep in task.depend_on_ids:
                if not dep.creation_plan and dep.id in date_map:
                    latest_end = max(latest_end, date_map[dep.id])
            start = latest_end + timedelta(days=1)
            end = start + timedelta(days=task.no_of_days or 0)
            task.planned_scheduled_start_date = start
            task.planned_scheduled_end_date = end
            date_map[task.id] = end

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            today = date.today()  
            new_state = vals['state']
            for task in self:
                if new_state == '1_done':
                    if not task.date_deadline:
                        task.date_deadline = today
                    dependent_tasks = self.env['project.task'].search([
                        ('depend_on_ids', 'in', task.id)
                    ])
                    for dep_task in dependent_tasks:
                        dep_task.actual_start_date = task.date_deadline + timedelta(days=1)
                        dep_task.actual_end_date = dep_task.actual_start_date + timedelta(days=dep_task.no_of_days)
                elif new_state == '01_in_progress' and not task.depend_on_ids:
                    if not task.actual_start_date:
                        task.actual_start_date = today
                        task.actual_end_date = task.actual_start_date + timedelta(days=task.no_of_days)
                else:
                    if task.date_deadline:
                        task.date_deadline = False
                    dependent_tasks = self.env['project.task'].search([
                        ('depend_on_ids', 'in', task.id),
                    ])
                    for dependent_task in dependent_tasks:
                        dependent_task.write({
                            'actual_start_date': False,
                            'actual_end_date': False
                        })
        return res
