
{
    "name": "FSPL Sales Costing Approval",
    "version": "2.0",
    "category": "Sales",
    "summary": "Custom Margin and Cost Calculation for Sales",
    "odoo_task_id": "4852586",
    "author": "Odoo PS-IN",
    "depends": [
        "base_address_extended",
        "sale_management",
        "purchase",
        "approvals",
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/approval_request_view.xml",
        "views/margin_master_view.xml",
        "views/discount_master_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_type_view.xml",
        "views/stock_picking_view.xml",
    ],
    "license": 'LGPL-3',
    "installable": True,
    "application": False
}
