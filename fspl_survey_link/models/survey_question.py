from odoo import api, fields, models, _


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_type = fields.Selection(
        selection_add=[('attachment', 'Attachment Upload')],
        ondelete={'attachment': 'cascade'},
    )

    is_attachment_given = fields.Boolean(default=False)

    @api.model
    def validate_question(self, answer, comment=None):
        """ Validate answer based on question type including attachment."""
        self.ensure_one()
        if isinstance(answer, str):
            answer = answer.strip()

        if self.question_type == 'attachment':
            self.ensure_one()
            if self.constr_mandatory and not answer:
                return {self.id: self.constr_error_msg or _('This question requires an attachment.')}
        return super().validate_question(answer, comment=comment)

    def _validate_attachment(self):
        """Validate attachment by checking is_attachment_given boolean."""
        self.ensure_one()
        if self.constr_mandatory and not self.is_attachment_given:
            return {self.id: self.constr_error_msg or _('This question requires an attachment.')}
        return {}
