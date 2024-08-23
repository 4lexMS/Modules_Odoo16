# my_custom_module/__manifest__.py
{
    'name': 'Informe de punto de venta',
    'version': '1.0',
    'summary': 'Reportes de Puntos de ventas',
    'description': 'Este módulo imprime reportes de arqueo de caja y egreso o ingreso de caja.',
    'author': 'Alex',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale', 'stock', ],
    'data': [
        'wizard2/arqueo_cajas.xml',
        'wizard2/egreso_caja.xml',
        'views/action_report.xml',
        'views/inherit_pos_bill.xml',
        'report/reporte_arqueo.xml',
        'report/reporte_egreso.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.report_assets_common': [
            'point_of_sale_reports/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
}