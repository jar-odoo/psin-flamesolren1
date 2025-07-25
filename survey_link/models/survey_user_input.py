from odoo import models, fields, api


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    task_id = fields.Many2one('project.task', string='Task')
    task_name = fields.Char(string="Task Name")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('survey_id') and not vals.get('task_id'):
                task = self.env['project.task'].sudo().search([('survey_id', '=', vals['survey_id'])], limit=1)
                if task:
                    vals['task_id'] = task.id
                    vals['task_name'] = task.name

        records = super().create(vals_list)

        for record in records:
            if record.task_id:
                record.task_id.sudo()._compute_survey_data()

        return records

    def write(self, vals):
        res = super().write(vals)
        tasks = self.mapped('task_id').sudo()
        for task in tasks:
            task._compute_survey_data()
        return res

    def unlink(self):
        tasks = self.mapped('task_id').sudo()
        res = super().unlink()
        for task in tasks:
            task._compute_survey_data()
        return res


    def _save_lines(self, question, answer, comment, overwrite_existing=False):
        if question.question_type == 'attachment':
            existing_lines = self.user_input_line_ids.filtered(lambda l: l.question_id == question)
            if overwrite_existing and existing_lines:
                existing_lines.unlink()

            if answer and answer.get('attachment_binary'):
                self.env['survey.user_input.line'].create({
                    'user_input_id': self.id,
                    'question_id': question.id,
                    'answer_type': 'attachment',
                    'value_attachment_binary': answer['attachment_binary'],
                    'value_attachment_filename': answer.get('filename'),
                    'skipped': False,
                })
            else:
                self.env['survey.user_input.line'].create({
                    'user_input_id': self.id,
                    'question_id': question.id,
                    'answer_type': False,
                    'skipped': True,
                })
        else:
            return super(SurveyUserInput, self)._save_lines(question, answer, comment, overwrite_existing)
