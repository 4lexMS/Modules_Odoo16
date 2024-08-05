# my_custom_module/__manifest__.py
{
    'name': 'Etiquetas del producto',
    'version': '1.0',
    'summary': 'Personalizar etiquetas de productos',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'views/action_reporte1.xml',
        'report/reporte1.xml',
    ],
    'installable': True,
    'application': True,
}
