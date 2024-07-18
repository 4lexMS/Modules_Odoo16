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
        'views/producto_form.xml',
        'security/ir.model.access.csv',
        'views/reporte1.xml',
        'views/action_reporte1.xml',
    ],
    'installable': True,
    'application': True,
}
