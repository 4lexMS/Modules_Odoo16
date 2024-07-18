# my_custom_module/models/product_template.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(string='Name', required=True)
    default_code = fields.Char(string='Internal Reference')
    list_price = fields.Float(string='Sales Price', default=1.0)

class ProductLayout(models.TransientModel):
    _inherit = 'product.label.layout'
    confirm_report = fields.Boolean(string="Confirmar Reporte")

    print_format = fields.Selection([
        ('report_cris', 'Reporte Cristal'),
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price'),
    ], string="Format", default='dymo', required=True)

    def process(self):
        for record in self:
            if record.print_format == 'report_cris':
                xml_id = 'etiquetas.action_report_product_label_no_barcode'
            else:
                # Llamar al método original
                return super(ProductLayout, self).process()

            # Procesar el reporte cuando es 'report_cris'
            try:
                report_action = self.env.ref(xml_id)
                if not report_action:
                    raise UserError(_("No se pudo encontrar el reporte con el ID: %s" % xml_id))

                products = self.env['product.template'].browse(self._context.get('active_ids', []))
                if not products:
                    raise UserError(_("No se encontraron productos para generar el reporte."))

                return report_action.report_action(products)
            except Exception as e:
                raise UserError(_("Error al intentar generar el reporte: %s" % str(e)))
