/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProjectTaskStateSelection } from "@project/components/project_task_state_selection/project_task_state_selection";

patch(ProjectTaskStateSelection.prototype, {

    setup() {
        super.setup();
        this.icons["05_to_do"] = "fa-lg fa fa-list-ul";
        this.colorButton["05_to_do"] = "btn-outline-secondary";
    },

    get options() {
        const states = super.options;
        if (this.props.record.data[this.props.name] != "04_waiting_normal") {
            states.unshift(["05_to_do", "To-Do"]);
            
        }
        return states;
    },
});
