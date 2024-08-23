{
    'name': 'Lista de precios de productos',
    'version': '16.0.1.0.0',
    'summary': 'Reporte lista de precios de productos',
    'description':  'Reporte lista de precios de productos',
    'author': 'Fabiola Auz',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'report_xlsx', 'stock'],
    'data': [
        'views/product_template_views.xml',
        'views/stock_picking_form_views.xml',
        'views/product_price_list_views.xml',
        'wizard/product_price_report_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
}
