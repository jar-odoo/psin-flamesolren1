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
            return {}

        if not answer and self.question_type not in ['simple_choice', 'multiple_choice']:
            if self.constr_mandatory and not self.survey_id.users_can_go_back:
                return {self.id: self.constr_error_msg or _('This question requires an answer.')}
        else:
            if self.question_type == 'char_box':
                return self._validate_char_box(answer)
            elif self.question_type == 'numerical_box':
                return self._validate_numerical_box(answer)
            elif self.question_type in ['date', 'datetime']:
                return self._validate_date(answer)
            elif self.question_type in ['simple_choice', 'multiple_choice']:
                return self._validate_choice(answer, comment)
            elif self.question_type == 'matrix':
                return self._validate_matrix(answer)
            elif self.question_type == 'scale':
                return self._validate_scale(answer)
        return {}

    def _validate_attachment(self):
        """Validate attachment by checking is_attachment_given boolean."""
        self.ensure_one()
        if self.constr_mandatory and not self.is_attachment_given:
            return {self.id: self.constr_error_msg or _('This question requires an attachment.')}
        return {}
