import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import "@survey/../tests/tours/certification_failure";

patch(registry.category("web_tour.tours").get("test_certification_failure"), {
    steps() {

        const originalSteps = super.steps();
        const index_retry = originalSteps.findIndex(
            (step) => step.trigger ==='a:contains("Retry")'
        );
        originalSteps.splice(
            index_retry,
        );
        return originalSteps;
    },
});
