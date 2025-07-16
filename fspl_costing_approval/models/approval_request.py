from odoo import fields, models

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    sale_order_id = fields.Many2one('sale.order', string='Related Quotation')

    def action_approve(self, approver=None):
        res = super().action_approve(approver)
        for req in self.filtered(lambda r: r.sale_order_id):
            order = req.sale_order_id
            order.action_unlock()
            order.discount_with_dc = order.discount_amount * order.dc_capacity_kwp
        return res

    def action_refuse(self, approver=None):
        res = super().action_refuse(approver)
        for req in self.filtered(lambda r: r.sale_order_id):
            order = req.sale_order_id
            order.action_unlock()
            order.approval_requested = False
            order.approval_request_id = False
        return res
