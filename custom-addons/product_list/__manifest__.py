{
    'name': 'Product Price XLSX Report',
    'version': '1.0',
    'summary': 'Personalizar reporte lista de productos',
    'description': 'Este módulo personaliza los reportes de lista de precios los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'report_xlsx'],
    'data': [
        'views/tree_product_inh.xml',
        'wizard/product_price_report_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
}
