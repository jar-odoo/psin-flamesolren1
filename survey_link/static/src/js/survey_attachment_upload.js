import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import SurveyFormWidget from "@survey/js/survey_form";

publicWidget.registry.SurveyFormWidget = SurveyFormWidget.extend({
    _submitForm: async function (options = {}) {
        var params = {};

        if (options.previousPageId) {
            params.previous_page_id = options.previousPageId;
        }
        if (options.nextSkipped) {
            params.next_skipped_page_or_question = true;
        }

        var route = "/survey/submit";
        if (this.options.isStartScreen) {
            route = "/survey/begin";
            if (this.options.questionsLayout === 'page_per_question') {
                this.$('.o_survey_main_title').fadeOut(400);
            }
        } else {
            var $form = this.$('form');
            var formData = new FormData($form[0]);

            if (!options.skipValidation) {
                if (!this._validateForm($form, formData)) {
                    return;
                }
            }

            this._prepareSubmitValues(formData, params);

            const fileInputs = this.el.querySelectorAll('input[type="file"][name="attachment_file"]');
            let index = 1;
            for (const input of fileInputs) {
                if (input.files.length > 0) {
                    const file = input.files[0];
                    const base64Data = await new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onload = (e) => resolve(e.target.result.split(',')[1]);
                        reader.readAsDataURL(file);
                    });

                    params[`attachment_answer_${index}`] = base64Data;
                    params[`attachment_filename_${index}`] = file.name;
                    params[`attachment_mimetype_${index}`] = file.type;

                    index += 1;
                }
            }
        }

        this.preventEnterSubmit = true;
        if (this.options.sessionInProgress) {
            this.fadeInOutDelay = 400;
            this.readonly = true;
        }

        const submitPromise = rpc(
            `${route}/${this.options.surveyToken}/${this.options.answerToken}`,
            params
        );

        if (!this.options.isStartScreen && this.options.scoringType === 'scoring_with_answers_after_page') {
            const [correctAnswers] = await submitPromise;
            if (Object.keys(correctAnswers).length && document.querySelector('.js_question-wrapper')) {
                this._showCorrectAnswers(correctAnswers, submitPromise, options);
                return;
            }
        }

        this._nextScreen(submitPromise, options);
    },
});
