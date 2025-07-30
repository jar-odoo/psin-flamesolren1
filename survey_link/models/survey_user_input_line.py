from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero
import textwrap


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    answer_type = fields.Selection(selection_add=[('attachment', 'Attachment')])
    value_attachment_binary = fields.Binary("Attachment File", readonly=True)
    value_attachment_filename = fields.Char("Attachment Filename", readonly=True)
    title = fields.Char("Question Title", compute='_compute_question_title', store=False)
    task_id = fields.Many2one('project.task', string='Task', related='user_input_id.task_id', store=True)

    @api.depends('question_id')
    def _compute_question_title(self):
        for record in self:
            record.title = record.question_id.title if record.question_id else ''


    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        for line in self:
            if (line.skipped == bool(line.answer_type)):
                raise ValidationError(_('A question can either be skipped or answered, not both.'))

            if line.answer_type == 'numerical_box' and float_is_zero(line.value_numerical_box, precision_digits=6):
                continue
            if line.answer_type == 'scale' and line.value_scale == 0:
                continue

            field_name = False
            if line.answer_type == 'suggestion':
                field_name = 'suggested_answer_id'
            elif line.answer_type == 'attachment':
                field_name = 'value_attachment_binary'
            elif line.answer_type:
                field_name = f'value_{line.answer_type}'

            if field_name and not line[field_name]:
                raise ValidationError(_('The answer must be in the right type.'))

    @api.depends(
        'answer_type', 'value_text_box', 'value_numerical_box',
        'value_char_box', 'value_date', 'value_datetime',
        'value_attachment_filename',
        'suggested_answer_id.value', 'matrix_row_id.value',
    )
    def _compute_display_name(self):
        for line in self:
            if line.answer_type == 'char_box':
                line.display_name = line.value_char_box
            elif line.answer_type == 'text_box' and line.value_text_box:
                line.display_name = textwrap.shorten(line.value_text_box, width=50, placeholder=" [...]")
            elif line.answer_type == 'numerical_box':
                line.display_name = line.value_numerical_box
            elif line.answer_type == 'date':
                line.display_name = fields.Date.to_string(line.value_date)
            elif line.answer_type == 'datetime':
                line.display_name = fields.Datetime.to_string(line.value_datetime)
            elif line.answer_type == 'scale':
                line.display_name = line.value_scale
            elif line.answer_type == 'suggestion':
                if line.matrix_row_id:
                    line.display_name = f'{line.suggested_answer_id.value}: {line.matrix_row_id.value}'
                else:
                    line.display_name = line.suggested_answer_id.value
            elif line.answer_type == 'attachment':
                line.display_name = line.value_attachment_filename or _('Attachment (No filename)')
            
            if not line.display_name:
                line.display_name = _('Skipped')
