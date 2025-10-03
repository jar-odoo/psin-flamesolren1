# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Flame Solren - Project Task Custom',
    'version': '1.0',
    'description': """
                    The planned scheduled start and end dates of each task are calculated based on the sales order 
                    confirmation date and the number of days specified for that task. When a task's state is changed
                    to In Progress or Done, its actual start and end dates—along with those of any dependent tasks 
                    are updated accordingly. This allows the system to determine whether a task was completed early
                    or delayed by comparing the actual and planned dates. In case of multiple tasks listed in Blocked 
                    By of any particular task, the parent task's actual start and end date will be based on the latest
                    of it's dependent (child) tasks, until then it will remain in the custom Waiting state.
                """,
    'odoo_task_id' : '4852712',
    'category': 'Customizations',
    'author': 'Odoo PS-IN',
    'depends': [
        'project',
        'sale_project',
    ],
    'data': [
        "views/project_task_views.xml",
        "views/project_project_stage_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'flame_solren_project_custom/static/src/project_task_state_selection.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
