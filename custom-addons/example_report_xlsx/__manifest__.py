{
    'name': 'Lista de reportes de ventas',
    'version': '16.0.1.0.0',
    'summary': 'Reporte lista de precios de productos',
    'description':  'Reporte lista de precios de productos',
    'author': 'Fabiola Auz',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'report_xlsx', 'stock', 'account', 'point_of_sale'],
    'data': [
        'views/product_template_views.xml',
        'views/stock_picking_form_views.xml',
        'views/account_move_customer.xml',
        'wizard/account_move_report_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
}
