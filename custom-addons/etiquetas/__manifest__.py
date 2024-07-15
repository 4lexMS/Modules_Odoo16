# my_custom_module/__manifest__.py
{
    'name': 'etiquetas',
    'version': '1.0',
    'summary': 'Personalizar etiquetas de productos',
    'description': 'Este módulo personaliza las etiquetas de los productos.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'views/product_template_views.xml',
        'views/product_label_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
