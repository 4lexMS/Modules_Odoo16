# my_custom_module/__manifest__.py
{
    'name': 'etiquetas',
    'version': '1.0',
    'summary': 'Personalizar etiquetas de productos',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'stock',],
    'data': [
        'views/formato_reporte.xml',
        'views/producto_etiqueta_form.xml',
        'views/producto_form.xml',
        'views/report_action_etiqueta.xml',
        'views/report_etiqueta.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
