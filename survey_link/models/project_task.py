from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError

from odoo.addons.project.models.project_task import CLOSED_STATES

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

                    task.sudo().survey_filled_once = True

        return super(ProjectTask, self).write(vals)
    
    
    @api.depends('survey_link')
    def _compute_survey_data(self):
        for task in self:
            survey_id = False
            survey_filled_once = False

            if task.survey_link:
                match = re.search(r'/survey/start/([^/?#]+)', task.survey_link)
                if match:
                    survey_token = match.group(1)
                    survey = self.env['survey.survey'].with_context(active_test=False).sudo().search(
                        [('access_token', '=', survey_token)],
                        limit=1
                    )
                    if survey:
                        survey_id = survey.id
                        user_input = self.env['survey.user_input'].sudo().search([
                            ('survey_id', '=', survey_id),
                            ('state', '=', 'done')
                        ], limit=1)

                        if user_input:
                            survey_filled_once = True

            task.survey_id = survey_id
            task.survey_filled_once = survey_filled_once

    def action_open_survey_link(self):
        self.ensure_one()

        pattern = r"^(https?://[\w\-.:]+)?/survey/start/[\w\-]+$"

        if not self.survey_link or not re.match(pattern, self.survey_link):
            raise ValidationError(_("Survey link is not valid. It must match /survey/start/<survey_token>/<project_id>"))

        url = self.survey_link + '/' + str(self.project_id.id)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

