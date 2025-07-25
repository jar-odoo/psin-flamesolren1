from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError

CLOSED_STATES = {
    '1_done': 'Done',
    '1_canceled': 'Cancelled',
}

class ProjectTask(models.Model):
    _inherit = 'project.task'

    survey_link = fields.Char(string="Survey Link")
    survey_id = fields.Many2one('survey.survey', string="Survey", compute="_compute_survey_data", store=True)
    survey_filled_once = fields.Boolean(string="Survey Already Filled", compute="_compute_survey_data", store=True)

    def write(self, vals):
        for task in self:
            new_state = vals.get('state', task.state)

            closed_states = ['03_approved'] + list(CLOSED_STATES.keys())
            if new_state in closed_states:
                if task.survey_id and not task.survey_filled_once:
                    # Check if survey.user_input exists for this task and is done
                    user_input = self.env['survey.user_input'].sudo().search([
                        ('survey_id', '=', task.survey_id.id),
                        ('task_id', '=', task.id),
                        ('state', '=', 'done')
                    ], limit=1)

                    if not user_input:
                        raise ValidationError(_("You cannot move to a closed state without completing the survey."))

                    # Optional: set flag if not already set
                    task.sudo().survey_filled_once = True

        return super(ProjectTask, self).write(vals)
    
    
    @api.depends('survey_link')
    def _compute_survey_data(self):
        for task in self:
            task.survey_id = False
            task.survey_filled_once = False

            if task.survey_link:
                match = re.search(r'/survey/start/([^/?#]+)', task.survey_link)
                if match:
                    survey_token = match.group(1)
                    survey = self.env['survey.survey'].with_context(active_test=False).sudo().search(
                        [('access_token', '=', survey_token)],
                        limit=1
                    )
                    if survey:
                        task.survey_id = survey.id
                        user_input = self.env['survey.user_input'].sudo().search([
                            ('survey_id', '=', survey.id),
                            ('state', '=', 'done')
                        ], limit=1)

                        if user_input:
                            task.survey_filled_once = True

    def action_open_survey_link(self):
        self.ensure_one()

        url = self.survey_link + '/' + str(self.project_id.id)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

