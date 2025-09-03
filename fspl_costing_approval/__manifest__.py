
{
    "name": "FSPL Sales Costing Approval",
    "version": "1.0",
    "category": "Sales",
    "summary": "Custom Margin and Cost Calculation for Sales",
    "odoo_task_id": "4852586",
    "author": "Odoo PS-IN",
    "depends": [
        "base_address_extended",
        "sale_management",
        "purchase",
        "approvals"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/approval_request_view.xml",
        "views/margin_master_view.xml",
        "views/discount_master_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    'license': 'OEEL-1',
}
