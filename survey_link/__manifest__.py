{
    'name': 'Survey task link',
    'version': '1.0',
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    'summary': 'Help connecting survey with task.',
    'depends': ['base', 'project', 'survey'],
    'data': [
        'views/survey_attachment_list_view.xml',
        'views/project_task_views.xml',
        'views/survey_question_attachment.xml',
        'views/survey_user_input_views.xml',
        'views/survey_templates_print.xml',
    ],
    'assets': {
        'survey.survey_assets': [
            'survey_link/static/src/js/survey_attachment_upload.js',
        ],
    },
}
