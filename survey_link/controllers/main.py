from odoo.addons.survey.controllers.main import Survey as SurveyController
from odoo import http, fields
from odoo.http import request
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class SurveyAttachmentController(SurveyController):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True, csrf=False)
    def survey_submit(self, survey_token, answer_token, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if answer_sudo.state == 'done':
            return {}, {'error': 'unauthorized'}

        questions, page_or_question_id = survey_sudo._get_survey_questions(
            answer=answer_sudo,
            page_id=post.get('page_id'),
            question_id=post.get('question_id')
        )

        attachment_index = 1
        for question in questions:
            if question.question_type == 'attachment':
                answer_key = f'attachment_answer_{attachment_index}'
                filename_key = f'attachment_filename_{attachment_index}'
                mimetype_key = f'attachment_mimetype_{attachment_index}'

                attachment_binary = post.get(answer_key)
                attachment_filename = post.get(filename_key)
                attachment_mimetype = post.get(mimetype_key)

                if attachment_binary and attachment_filename:
                    post[str(question.id)] = {
                        'attachment_binary': attachment_binary,
                        'filename': attachment_filename,
                        'mimetype': attachment_mimetype,
                    }
                else:
                    post[str(question.id)] = {}

                attachment_index += 1  # Move to next file

        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(
                answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            return {}, {'error': 'unauthorized'}

        if answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached:
            if answer_sudo.question_time_limit_reached:
                time_limit = survey_sudo.session_question_start_time + relativedelta(
                    seconds=survey_sudo.session_question_id.time_limit
                )
                time_limit += timedelta(seconds=3)
            else:
                time_limit = answer_sudo.start_datetime + timedelta(minutes=survey_sudo.time_limit)
                time_limit += timedelta(seconds=10)
            if fields.Datetime.now() > time_limit:
                return {}, {'error': 'unauthorized'}

        errors = {}
        for question in questions:
            inactive_questions = request.env['survey.question'] if answer_sudo.is_session_answer else answer_sudo._get_inactive_conditional_questions()
            if question in inactive_questions:
                continue
            answer, comment = self._extract_comment_from_answers(question, post.get(str(question.id)))
            errors.update(question.validate_question(answer, comment))
            if not errors.get(question.id):
                answer_sudo._save_lines(
                    question, answer, comment,
                    overwrite_existing=survey_sudo.users_can_go_back or
                                       question.save_as_nickname or question.save_as_email
                )

        if errors and not (answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached):
            return {}, {'error': 'validation', 'fields': errors}

        if not answer_sudo.is_session_answer:
            answer_sudo._clear_inactive_conditional_answers()

        correct_answers = {}
        if survey_sudo.scoring_type == 'scoring_with_answers_after_page':
            scorable_questions = (questions - answer_sudo._get_inactive_conditional_questions()).filtered('is_scored_question')
            correct_answers = scorable_questions._get_correct_answers()

        if answer_sudo.survey_time_limit_reached or survey_sudo.questions_layout == 'one_page':
            answer_sudo._mark_done()
        elif 'previous_page_id' in post:
            answer_sudo.last_displayed_page_id = post['previous_page_id']
            return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, **post)
        elif 'next_skipped_page_or_question' in post:
            answer_sudo.last_displayed_page_id = page_or_question_id
            return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, next_skipped_page=True)
        else:
            if not answer_sudo.is_session_answer:
                page_or_question = request.env['survey.question'].sudo().browse(page_or_question_id)
                if answer_sudo.survey_first_submitted and answer_sudo._is_last_skipped_page_or_question(page_or_question):
                    next_page = request.env['survey.question']
                else:
                    next_page = survey_sudo._get_next_page_or_question(answer_sudo, page_or_question_id)
                if not next_page:
                    if survey_sudo.users_can_go_back and answer_sudo.user_input_line_ids.filtered(
                            lambda a: a.skipped and a.question_id.constr_mandatory):
                        answer_sudo.write({
                            'last_displayed_page_id': page_or_question_id,
                            'survey_first_submitted': True,
                        })
                        return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, next_skipped_page=True)
                    else:
                        answer_sudo._mark_done()

            answer_sudo.last_displayed_page_id = page_or_question_id

        return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo)

    def _extract_comment_from_answers(self, question, answers):
        comment = None
        answers_no_comment = []

        if question.question_type == 'attachment':
            if answers and isinstance(answers, dict):
                binary_data = answers.get('attachment_binary')
                filename = answers.get('filename')
                return {'attachment_binary': binary_data, 'filename': filename}, comment

        if answers:
            if question.question_type == 'matrix':
                if 'comment' in answers:
                    comment = answers['comment'].strip()
                    answers.pop('comment')
                answers_no_comment = answers
            else:
                if not isinstance(answers, list):
                    answers = [answers]
                for answer in answers:
                    if isinstance(answer, dict) and 'comment' in answer:
                        comment = answer['comment'].strip()
                    else:
                        answers_no_comment.append(answer)
                if len(answers_no_comment) == 1:
                    answers_no_comment = answers_no_comment[0]
        return answers_no_comment, comment

    @http.route(['/survey/start/<string:survey_token>/<int:project_id>'], type='http', auth='public', website=True)
    def start_survey_with_project(self, survey_token, project_id, **post):
        request.session['project_id'] = project_id
        return request.redirect('/survey/start/' + survey_token)

    @http.route(['/survey/start/<string:survey_token>'], type='http', auth='public', website=True)
    def survey_start(self, survey_token, **post):
        SurveyUserInput = request.env['survey.user_input'].sudo()
        survey = request.env['survey.survey'].sudo().search([('access_token', '=', survey_token)], limit=1)

        if not survey:
            return request.redirect('/')

        project_id = request.session.get('project_id')

        domain = [('survey_id', '=', survey.id), ('state', '=', 'done')]
        if project_id:
            domain.append(('project_id', '=', project_id))

        user_input = SurveyUserInput.search(domain, limit=1)

        if user_input:
            return request.redirect(f'/survey/already_filled/{user_input.access_token}')
        else:
            return super(SurveyAttachmentController, self).survey_start(survey_token, **post)

    @http.route(['/survey/already_filled/<string:token>'], type='http', auth='public', website=True)
    def already_filled_page(self, token, **post):
        user_input = request.env['survey.user_input'].sudo().search([('access_token', '=', token)], limit=1)

        if not user_input:
            return request.redirect('/')

        survey = user_input.survey_id

        return request.render('survey_link.already_filled_template', {
            'survey': survey,
            'user_input': user_input,
        })
