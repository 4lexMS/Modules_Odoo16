from odoo import models, fields, api
import xlsxwriter
import base64
from io import BytesIO

class ProductListSale(models.Model):
    _inherit = 'account.move'

    def action_button_account_customer(self):
        bill_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')]).ids
        ctx = dict(self.env.context or {}, active_ids=bill_ids)
        view = self.env.ref('example_report_xlsx.view_account_move_report_wizard', False)

        return {
            'name': 'Listar precios Ventas',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'account.move.report.wizard',
            'target': 'new',
            'context': ctx,
        }

class ProductListTrans(models.Model):
    _inherit = 'stock.picking'

    def action_button_list_trans(self):
        product_ids = self.env['stock.move'].search([('picking_id', '=', self.id)]).mapped('product_tmpl_id').ids
        ctx = dict(self.env.context or {}, active_ids=product_ids)
        view = self.env.ref('example_report_xlsx.view_account_move_report_wizard', False)
        return {
            'name': 'Listar precios Transferencia',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'account.move.report.wizard',
            'target': 'new',
            'context': ctx,
        }

class AccountMoveReportWizard(models.TransientModel):
    _name = 'account.move.report.wizard'
    _description = 'Reporte de Facturas'
    session_id = fields.Many2one('pos.session', string="Sesión", required=True)

    report_type = fields.Selection([
        ('type1', 'Reporte Venta Detallado'),
        ('type2', 'Reporte Venta Detallado con Faltante'),
        ('type3', 'Reporte Venta Resumido'),
    ], string='Tipo de reporte', required=True)

    def generate_report(self):
        self.ensure_one()
        session_id = self.session_id.id

        query = """
            SELECT ---buscar las facturas al contado
                po.pos_reference AS ingreso_doc,
                po.name AS tipo_doc,
                am.name AS documento,
                am.invoice_partner_display_name AS referencia,
                am.amount_total AS valor_total,
                ps.name AS sesion,
                NULL AS total_res,
                acj.type AS tipo_pago

            FROM
                account_move am
            INNER JOIN
                pos_order po ON po.account_move = am.id
            INNER JOIN
                pos_session ps ON po.session_id = ps.id
            INNER JOIN
                pos_payment pp ON pp.pos_order_id = po.id
            INNER JOIN
                pos_payment_method pm ON pm.id = pp.payment_method_id
            INNER JOIN
                account_journal acj ON acj.id = pm.journal_id
            WHERE
                am.move_type = 'out_invoice'
                AND ps.id = %s

            UNION ALL
                ---buscar las salidas en efectivo de la sesion seleccionada

            SELECT
                am.name AS ingreso_doc,
                NULL AS tipo_doc,
                NULL AS documento,
                cbk.payment_ref AS referencia,
                cbk.amount AS valor_total,
                ps.name AS sesion,
                cbk.amount_residual AS total_res,
                NULL AS tipo_pago

            FROM
                account_move am
            INNER JOIN
                pos_session ps ON am.id = ps.move_id
            INNER JOIN
                account_bank_statement_line cbk ON ps.id = cbk.pos_session_id
            INNER JOIN
                account_journal acj ON acj.id = am.journal_id
            WHERE
                cbk.amount < 0
                AND ps.id = %s
            ORDER BY
                sesion, tipo_doc
        """

        self.env.cr.execute(query, (session_id, session_id))
        invoice = self.env.cr.dictfetchall()

        if self.report_type == "type1":
            return self.action_generate_xlsx_report1(invoice)
        elif self.report_type == "type2":
            return self.action_generate_xlsx_report2(invoice)
        else:
            return self.action_generate_xlsx_report3(invoice)

    def action_generate_xlsx_report1(self, data):
        # Crear un archivo XLSX en memoria

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')
        worksheet.hide_gridlines(option=2)

        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 14,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True
            })

        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            })

        title_header1 = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "underline": 1  # Agregar subrayado
            })

        title_price = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
            })

        text_price = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_price2 = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        borderformat = workbook.add_format({
            'text_wrap': True,
            'bottom': 2
        })

        worksheet.set_row(0, 25)
        worksheet.set_row(1, 20.5)
        worksheet.set_row(2, 18)
        worksheet.set_row(3, 18)
        worksheet.set_column('A:A', 4.8)
        worksheet.set_column('B:B', 0.1)
        worksheet.set_column('C:C', 10.4)
        worksheet.set_column('D:D', 0.9)
        worksheet.set_column('E:E', 1.5)
        worksheet.set_column('F:F', 0.6)

        worksheet.set_column('G:K', 0.1)
        worksheet.set_column('L:L', 0.6)
        worksheet.set_column('M:M', 3)
        worksheet.set_column('N:N', 0.6)
        worksheet.set_column('O:O', 1)
        worksheet.set_column('P:P', 3.8)
        worksheet.set_column('Q:Q', 0.1)
        worksheet.set_column('R:R', 3.5)
        worksheet.set_column('S:T', 0.1)
        worksheet.set_column('U:U', 1.8)
        worksheet.set_column('V:V', 0.7)
        worksheet.set_column('W:W', 0.1)
        worksheet.set_column('X:X', 4)
        worksheet.set_column('Y:Y', 0.1)
        worksheet.set_column('Z:Z', 5.6)
        worksheet.set_column('AA:AA', 5)
        worksheet.set_column('AB:AC', 0.1)
        worksheet.set_column('AD:AD', 10)
        worksheet.set_column('AE:AE', 1)
        worksheet.set_column('AF:AF', 0.1)
        worksheet.set_column('AG:AG', 10)
        worksheet.set_column('AH:AH', 10)

        for row_buc in range(1, 9):
            worksheet.set_row(row_buc, 12)

        worksheet.merge_range('B1:AH1', 'Reporte  Diario de Caja ', title_format)
        worksheet.merge_range('C2:AD2', 'IGC- INGRESOS A CAJA ', title_header1)
        worksheet.merge_range('C3:AD3', 'FACTURAS CONTADO', title_header)

        headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
        header_ranges = ['C4', 'D4:M4', 'N4:W4', 'X4:AD4', 'AE4:AG4']

        # Escribir los encabezados
        for header, cell_range in zip(headers, header_ranges):
            if header == 'Valor':
                # Aplica text_price al encabezado 'Valor'
                format_to_use = title_price
            else:
                # Aplica title_header a los demás encabezados
                format_to_use = title_header

            if ':' in cell_range:  # Si es un rango (por ejemplo, D4:M4)
                worksheet.merge_range(cell_range, header, format_to_use)
            else:  # Si es una sola celda (por ejemplo, C4)
                worksheet.write(cell_range, header, format_to_use)

                row = 4
                sumaIGC = 0
                max_data_row = 56  # Última fila para datos

        for invoice in data:
            if row > max_data_row:
                break
            worksheet.set_row(row, 12)
            if invoice.get('tipo_pago') == 'cash':
                worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                worksheet.merge_range(row, 30, row, 32, invoice.get('valor_total', 0), text_price)
                row += 1
                sumaIGC += invoice.get('valor_total', 0)

        #si son mas de 50 productos
        if len(data) > (max_data_row - 3):
            worksheet.merge_range('B58:AH58', 'Reporte Diario de Caja', title_format)
            row = 58

            for invoice in data[max_data_row - 3:]:
                worksheet.set_row(row, 12)
                if invoice.get('tipo_pago') == 'cash':
                    worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                    worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                    worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                    worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                    worksheet.merge_range(row, 30, row, 32, invoice.get('valor_total', 0), text_price)
                    row += 1
                    sumaIGC += invoice.get('valor_total', 0)

            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaIGC,  text_price)            
            worksheet.merge_range(row+1, 23, row+1, 29,  'TOTAL IGC',  title_price)
            worksheet.merge_range(row+1, 30, row+1, 32,  sumaIGC,  text_price2)
            worksheet.merge_range(row+2, 2, row+2, 29,  'EGC- EGRESOS DE CAJA',  title_header1)
            worksheet.merge_range(row+3, 2, row+3, 29,  'DEPOSITO BANCARIO(6)',  title_header)

            headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor'] #EGRESOS
            header_ranges = [(row+4, 2),
                             (row+4, 3, row+4, 12),
                             (row+4, 13, row+4, 22),
                             (row+4, 23, row+4, 29),
                             (row+4, 30, row+4, 32)
                             ]

            # Escribir los encabezados
            for header, cell_range in zip(headers, header_ranges):
                if header == 'Valor':
                    # Aplica text_price al encabezado 'Valor'
                    format_to_use = title_price
                else:
                    # Aplica title_header a los demás encabezados
                    format_to_use = title_header

                if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                    worksheet.merge_range(*cell_range, header, format_to_use)
                elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                    worksheet.write(cell_range[0], cell_range[1], header, format_to_use)

            row = row+5
            sumaEGBC = 0
            sumaTEG = 0

            for invoice in data:
                worksheet.set_row(row, 15)
                if invoice.get('valor_total') < 0:
                    worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                    worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                    worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                    worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                    worksheet.merge_range(row, 30, row, 32, invoice.get('total_res', 0), text_price)
                    row += 1
                    sumaIGC += invoice.get('total_res', 0)
                    sumaTEG += invoice.get('total_res', 0)

            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaEGBC,  text_price)
            worksheet.merge_range(row+1, 2, row+1, 29,  'OTROS EGRESOS(3)',  title_header)

            headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
            header_ranges = [(row+2, 2),
                             (row+2, 3, row+2, 12),
                             (row+2, 13, row+2, 22),
                             (row+2, 23, row+2, 29),
                             (row+2, 30, row+2, 32)
                             ]

            # Escribir los encabezados
            for header, cell_range in zip(headers, header_ranges):
                if header == 'Valor':
                    # Aplica text_price al encabezado 'Valor'
                    format_to_use = title_price
                else:
                    # Aplica title_header a los demás encabezados
                    format_to_use = title_header

                if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                    worksheet.merge_range(*cell_range, header, format_to_use)
                elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                    worksheet.write(cell_range[0], cell_range[1], header, format_to_use)
            row = row+3
            sumaOEG = 0

            for invoice in data:
                if invoice.get('valor_total') < 0:
                    worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                    worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                    worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                    worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                    worksheet.merge_range(row, 30, row, 32, invoice.get('total_res', 0), text_price)
                    row += 1
                    sumaOEG += invoice.get('total_res', 0)
                    sumaTEG += invoice.get('total_res', 0)

            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaOEG,  text_price)
            worksheet.merge_range(row+1, 23, row+1, 29,  'TOTAL EGC', title_price)
            worksheet.merge_range(row+1, 30, row+1, 32,  sumaTEG,  text_price2)

        else:
            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaIGC,  text_price)            
            worksheet.merge_range(row+1, 23, row+1, 29,  'TOTAL IGC',  title_price)
            worksheet.merge_range(row+1, 30, row+1, 32,  sumaIGC,  text_price2)
            worksheet.merge_range(row+2, 2, row+2, 29,  'EGC- EGRESOS DE CAJA',  title_header1)
            worksheet.merge_range(row+3, 2, row+3, 29,  'DEPOSITO BANCARIO(6)',  title_header)

            headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
            header_ranges = [(row+4, 2),
                             (row+4, 3, row+4, 12),
                             (row+4, 13, row+4, 22),
                             (row+4, 23, row+4, 29),
                             (row+4, 30, row+4, 32)
                             ]

            # Escribir los encabezados
            for header, cell_range in zip(headers, header_ranges):
                if header == 'Valor':
                    # Aplica text_price al encabezado 'Valor'
                    format_to_use = title_price
                else:
                    # Aplica title_header a los demás encabezados
                    format_to_use = title_header

                if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                    worksheet.merge_range(*cell_range, header, format_to_use)
                elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                    worksheet.write(cell_range[0], cell_range[1], header, format_to_use)

            row = row+5
            sumaEGBC = 0
            sumaTEG = 0

            for invoice in data:
                worksheet.set_row(row, 20)
                if invoice.get('valor_total') < 0:
                    worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                    worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                    worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                    worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                    worksheet.merge_range(row, 30, row, 32, invoice.get('total_res', 0), text_price)
                    row += 1
                    sumaEGBC += invoice.get('total_res', 0)
                    sumaTEG += invoice.get('total_res', 0)

            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaEGBC,  text_price)
            worksheet.merge_range(row+1, 2, row+1, 29,  'OTROS EGRESOS(3)',  title_header)

            headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
            header_ranges = [(row+2, 2),
                             (row+2, 3, row+2, 12),
                             (row+2, 13, row+2, 22),
                             (row+2, 23, row+2, 29),
                             (row+2, 30, row+2, 32)
                             ]

            # Escribir los encabezados
            for header, cell_range in zip(headers, header_ranges):
                if header == 'Valor':
                    # Aplica text_price al encabezado 'Valor'
                    format_to_use = title_price
                else:
                    # Aplica title_header a los demás encabezados
                    format_to_use = title_header

                if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                    worksheet.merge_range(*cell_range, header, format_to_use)
                elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                    worksheet.write(cell_range[0], cell_range[1], header, format_to_use)
            row = row+3
            sumaOEG = 0

            for invoice in data:
                worksheet.set_row(row, 20)
                if invoice.get('valor_total') < 0:
                    worksheet.write(row, 2, invoice.get('ingreso_doc', ""), text_products)
                    worksheet.merge_range(row, 3, row, 12, invoice.get('tipo_doc', ""), text_products)
                    worksheet.merge_range(row, 13, row, 22, invoice.get('documento', ""), text_products)
                    worksheet.merge_range(row, 23, row, 29, invoice.get('referencia', ""), text_products)
                    worksheet.merge_range(row, 30, row, 32, invoice.get('total_res', 0), text_price)
                    row += 1
                    sumaOEG += invoice.get('total_res', 0)
                    sumaTEG += invoice.get('total_res', 0)

            worksheet.merge_range(row, 26, row, 29,  'Total', title_price)
            worksheet.merge_range(row, 30, row, 32,  sumaOEG,  text_price)
            worksheet.merge_range(row+1, 23, row+1, 29,  'TOTAL EGC', title_price)
            worksheet.merge_range(row+1, 30, row+1, 32,  sumaTEG,  text_price2)

        worksheet.merge_range(row+2, 1, row+2, 33, 'Reporte  Diario de Caja ', title_format)
        worksheet.set_row(row+3, 1)
        worksheet.merge_range(row+3, 2, row+3, 10, '', borderformat)
        worksheet.merge_range(row+4, 2, row+4, 17, 'Ingresos a Caja ', title_header)
        worksheet.merge_range(row+5, 1, row+5, 11, 'Tipo Emitido ', title_header)
        worksheet.merge_range(row+5, 12, row+5, 21, 'Valor', title_price)
        worksheet.set_row(row+6, 1)
        worksheet.merge_range(row+6, 1, row+6, 21, '', borderformat)

        worksheet.merge_range(row+7, 1, row+7, 11, 'Facturas Contado', text_products)
        worksheet.merge_range(row+7, 12, row+7, 21, sumaIGC, text_price)
        worksheet.merge_range(row+8, 1, row+8, 11, 'Facturas Crédito', text_products)
        worksheet.merge_range(row+8, 12, row+8, 21, invoice.get('total_res', 0), text_price)
        sumaIGC2 = sumaIGC + invoice.get('total_res', 0)
        worksheet.merge_range(row+9, 1, row+9, 11, 'Cobros a Clientes', text_products)
        worksheet.merge_range(row+9, 12, row+9, 21, invoice.get('total_res', 0), text_price)
        sumaIGC2 += invoice.get('total_res', 0)
        worksheet.merge_range(row+10, 1, row+10, 11, 'Ingresos Banco', text_products)
        worksheet.merge_range(row+10, 12, row+10, 21, invoice.get('total_res', 0), text_price)
        sumaIGC2 += invoice.get('total_res', 0)
        worksheet.merge_range(row+11, 1, row+11, 11, 'Otros Ingresos', text_products)
        worksheet.merge_range(row+11, 12, row+11, 21, invoice.get('total_res', 0), text_price)
        sumaIGC2 += invoice.get('total_res', 0)
        worksheet.merge_range(row+12, 1, row+12, 11, 'Total ', title_price)
        worksheet.merge_range(row+12, 12, row+12, 21, sumaIGC2, text_price2)

        worksheet.merge_range(row+13, 2, row+13, 17, 'Egresos de Caja ', title_header)
        worksheet.merge_range(row+14, 2, row+14, 7, 'Tipo Emitido ', title_header)
        worksheet.merge_range(row+14, 10, row+14, 19, 'Valor', title_price)
        worksheet.set_row(row+15, 1)
        worksheet.merge_range(row+15, 2, row+15, 19, '', borderformat)
        worksheet.set_row(row+16, 1)
        worksheet.merge_range(row+17, 2, row+17, 8, 'OTROS EGRESOS(3)', text_products)
        worksheet.merge_range(row+17, 10, row+17, 18,  sumaOEG,  text_price)
        worksheet.merge_range(row+18, 2, row+18, 8, 'DEPOSITO BANCARIO(6)', text_products)
        worksheet.merge_range(row+18, 10, row+18, 18,  sumaEGBC,  text_price)
        worksheet.set_row(row+19, 1)
        worksheet.merge_range(row+20, 2, row+20, 8, 'Total:', title_price)
        worksheet.merge_range(row+20, 10, row+20, 18,  sumaTEG,  text_price2)
        worksheet.set_row(row+21, 1)
        worksheet.merge_range(row+22, 2, row+22, 14, 'Formas de Pago General', title_header)
        worksheet.merge_range(row+23, 2, row+23, 4, 'Formas de Pago', title_header)
        worksheet.merge_range(row+23, 7, row+23, 15, 'Apertura', title_price)
        worksheet.merge_range(row+23, 17, row+23, 23, 'Valor Ingreso', title_price)
        worksheet.merge_range(row+23, 25, row+23, 27, 'Valor Egreso', title_price)
        worksheet.merge_range(row+23, 29, row+23, 31, 'Saldo', title_price)
        worksheet.set_row(row+24, 1)
        worksheet.merge_range(row+24, 2, row+24, 30, '', borderformat)

        row = row+25
        sumaToIn = 0
        sumaToEg = 0

        for invoice in data:
            worksheet.set_row(row, 12)
            worksheet.merge_range(row, 2, row, 4, invoice.get('tipo_doc', ""), text_products)
            worksheet.merge_range(row, 7, row, 15, invoice.get('valor_total'), text_price)
            worksheet.merge_range(row, 17, row, 23, invoice.get('total_res', 0), text_price)
            worksheet.merge_range(row, 25, row, 27, invoice.get('total_res', 0), text_price)
            #valor = apertura + ingresos - egresos
            worksheet.merge_range(row, 29, row, 31, invoice.get('valor_total', 0), text_products)
            row += 1
            sumaToIn += invoice.get('total_res', 0) or 0
            sumaToEg += invoice.get('total_res', 0) or 0

        worksheet.merge_range(row, 7, row, 15, 'TOTALES', text_price2)
        #VALOR INGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 17, row, 23, sumaToIn, text_price2)
        #VALOR EGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 25, row, 28, sumaToEg, text_price2)
        worksheet.merge_range(row+1, 2, row+1, 20, 'Formas de Pago de Facturas Contado', title_header)
        worksheet.merge_range(row+2, 2, row+2, 4, 'Formas de Pago', title_header)
        worksheet.merge_range(row+2, 7, row+2, 15, 'Valor', title_price)
        worksheet.set_row(row+3, 1)
        worksheet.merge_range(row+3, 2, row+3, 15, '', borderformat)

        row = row + 4
        total_ef = 0

        for invoice in data:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.merge_range(row, 2, row, 4, invoice.get('tipo_doc', ""), text_products)
            #VALOR FORMAS DE PAGO
            worksheet.merge_range(row, 7, row, 15, invoice.get('total_res', 0), text_price)
            row += 1
            total_ef += invoice.get('total_res', 0) or 0
        worksheet.merge_range(row, 2, row, 3, 'Totales', text_price2)
        worksheet.merge_range(row, 7, row, 15, total_ef, text_price2)

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'Reporte Diario de Venta detalllado.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
    def action_generate_xlsx_report2(self, products):
        # Crear un archivo XLSX en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')
        worksheet.hide_gridlines(option=2)

        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 14,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True
            })

        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            })

        title_header1 = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "underline": 1  # Agregar subrayado
            })

        title_price = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
            })

        text_price = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_price2 = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        borderformat = workbook.add_format({
            'text_wrap': True,
            'bottom': 2
        })

        worksheet.set_row(0, 25)
        worksheet.set_row(1, 20.5)
        worksheet.set_row(2, 18)
        worksheet.set_row(3, 18)
        worksheet.set_column('A:A', 4.8)
        worksheet.set_column('B:B', 0.1)
        worksheet.set_column('C:C', 10.4)
        worksheet.set_column('D:D', 0.9)
        worksheet.set_column('E:E', 1.5)
        worksheet.set_column('F:F', 0.6)

        worksheet.set_column('G:K', 0.1)
        worksheet.set_column('L:L', 0.6)
        worksheet.set_column('M:M', 3)
        worksheet.set_column('N:N', 0.6)
        worksheet.set_column('O:O', 1)
        worksheet.set_column('P:P', 3.8)
        worksheet.set_column('Q:Q', 0.1)
        worksheet.set_column('R:R', 3.5)
        worksheet.set_column('S:T', 0.1)
        worksheet.set_column('U:U', 1.8)
        worksheet.set_column('V:V', 0.7)
        worksheet.set_column('W:W', 0.1)
        worksheet.set_column('X:X', 4)
        worksheet.set_column('Y:Y', 0.1)
        worksheet.set_column('Z:Z', 5.6)
        worksheet.set_column('AA:AA', 5)
        worksheet.set_column('AB:AC', 0.1)
        worksheet.set_column('AD:AD', 10)
        worksheet.set_column('AE:AE', 1)
        worksheet.set_column('AF:AF', 0.1)
        worksheet.set_column('AG:AG', 10)
        worksheet.set_column('AH:AH', 10)

        for row_buc in range(1, 20):
            worksheet.set_row(row_buc, 12)

        worksheet.merge_range('B1:AH1', 'Reporte  Diario de Caja ', title_format)
        worksheet.merge_range('C2:AD2', 'NOTAS DE CREDITO ', title_header1)
        worksheet.merge_range('C3:AD3', 'Notas de Credito de Clientes (FAC)', title_header)

        headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
        header_ranges = ['C4', 'D4:M4', 'N4:W4', 'X4:AD4', 'AE4:AG4']

        # Escribir los encabezados
        for header, cell_range in zip(headers, header_ranges):
            if header == 'Valor':
                # Aplica text_price al encabezado 'Valor'
                format_to_use = title_price
            else:
                # Aplica title_header a los demás encabezados
                format_to_use = title_header

            if ':' in cell_range:  # Si es un rango (por ejemplo, D4:M4)
                worksheet.merge_range(cell_range, header, format_to_use)
            else:  # Si es una sola celda (por ejemplo, C4)
                worksheet.write(cell_range, header, format_to_use)

        row = 4
        #TOTAL NOTAS DE CREDITO
        total_NC = 0

        for product in products:

            worksheet.set_row(row, 12)  # Establece la altura de la fila en 12 puntos
            worksheet.write(row, 2, product.barcode if product.barcode else "-", text_products)
            worksheet.merge_range(row, 3, row, 12, product.list_price, text_products)
            worksheet.merge_range(row, 13, row, 22, product.name, text_products)
            worksheet.merge_range(row, 23, row, 29, product.name, text_products)
            worksheet.merge_range(row, 30, row, 32, product.list_price, text_price)
            row += 1
            total_NC += product.list_price

        worksheet.merge_range(row, 26, row, 29, 'Total', text_price2)
        worksheet.merge_range(row, 30, row, 32, total_NC, text_price)
        worksheet.merge_range(row+1, 23, row+1, 29, 'TOTAL NOTAS DE CREDITO', title_price)
        worksheet.merge_range(row+1, 30, row+1, 32, total_NC, text_price2)
        worksheet.merge_range(row+2, 2, row+2, 29, 'IGC- INGRESOS A CAJA', title_header1)
        worksheet.merge_range(row+3, 2, row+3, 29, 'FACTURAS CONTADO', title_header)

        headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
        header_ranges = [(row+4, 2),
                         (row+4, 3, row+4, 12),
                         (row+4, 13, row+4, 22),
                         (row+4, 23, row+4, 29),
                         (row+4, 30, row+4, 32)
                         ]

        for header, cell_range in zip(headers, header_ranges):
            if header == 'Valor':
                # Aplica text_price al encabezado 'Valor'
                format_to_use = title_price
            else:
                # Aplica title_header a los demás encabezados
                format_to_use = title_header

            if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                worksheet.merge_range(*cell_range, header, format_to_use)
            elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                worksheet.write(cell_range[0], cell_range[1], header, format_to_use)
        row += 5
        #TOTAL FACTURAS CONTADO
        total_fact_c = 0

        for product in products:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 2, product.barcode if product.barcode else "-", text_products)
            worksheet.merge_range(row, 3, row, 12, product.list_price, text_products)
            worksheet.merge_range(row, 13, row, 22, product.name, text_products)
            worksheet.merge_range(row, 23, row, 29, product.name, text_products)
            worksheet.merge_range(row, 30, row, 32, product.list_price, text_price)
            row += 1
            total_fact_c += product.list_price
        worksheet.merge_range(row, 26, row, 29, 'Total', text_price2)
        worksheet.merge_range(row, 30, row, 32, total_fact_c, text_price)
        worksheet.merge_range(row+1, 2, row+1, 29, 'FACTURAS CREDITO', title_header)

        headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
        header_ranges = [(row+2, 2),
                         (row+2, 3, row+2, 12),
                         (row+2, 13, row+2, 22),
                         (row+2, 23, row+2, 29),
                         (row+2, 30, row+2, 32)
                         ]

        for header, cell_range in zip(headers, header_ranges):
            if header == 'Valor':
                # Aplica text_price al encabezado 'Valor'
                format_to_use = title_price
            else:
                # Aplica title_header a los demás encabezados
                format_to_use = title_header

            if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                worksheet.merge_range(*cell_range, header, format_to_use)
            elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                worksheet.write(cell_range[0], cell_range[1], header, format_to_use)

        row += 3
        #Total facturas credito
        total_fact_c2 = 0
        totalIGC = total_fact_c

        for product in products:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 2, product.barcode if product.barcode else "-", text_products)
            worksheet.merge_range(row, 3, row, 12, product.list_price, text_products)
            worksheet.merge_range(row, 13, row, 22, product.name, text_products)
            worksheet.merge_range(row, 23, row, 29, product.name, text_products)
            worksheet.merge_range(row, 30, row, 32, product.list_price, text_price)
            row += 1
            total_fact_c2 += product.list_price
            totalIGC += product.list_price
        worksheet.merge_range(row, 26, row, 29, 'Total', text_price2)
        worksheet.merge_range(row, 30, row, 32, total_fact_c2, text_price)
        worksheet.merge_range(row+1, 23, row+1, 29, 'TOTAL IGC', title_price)
        worksheet.merge_range(row+1, 30, row+1, 32, totalIGC, text_price2)
        worksheet.merge_range(row+2, 2, row+2, 29, 'EGC- EGRESOS DE CAJA', title_header1)
        worksheet.set_row(row+3, 20)
        worksheet.merge_range(row+3, 1, row+3, 33, 'Reporte Diario de Caja', title_format)
        worksheet.merge_range(row+4, 2, row+4, 29, 'OTROS EGRESOS(3)', title_header)

        headers = ['No. Ingreso', 'Tipo', 'Documento', 'Referencia', 'Valor']
        header_ranges = [(row+5, 2),
                         (row+5, 3, row+5, 12),
                         (row+5, 13, row+5, 22),
                         (row+5, 23, row+5, 29),
                         (row+5, 30, row+5, 32)
                         ]

        for header, cell_range in zip(headers, header_ranges):
            if header == 'Valor':
                # Aplica text_price al encabezado 'Valor'
                format_to_use = title_price
            else:
                # Aplica title_header a los demás encabezados
                format_to_use = title_header

            if isinstance(cell_range, tuple) and len(cell_range) == 4:  # Si es un rango (por ejemplo, (row+4, 3, row+4, 12))
                worksheet.merge_range(*cell_range, header, format_to_use)
            elif isinstance(cell_range, tuple) and len(cell_range) == 2:  # Si es una sola celda (por ejemplo, (row+4, 2))
                worksheet.write(cell_range[0], cell_range[1], header, format_to_use)

        row += 6
        total_OE = 0

        for product in products:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.write(row, 2, product.barcode if product.barcode else "-", text_products)
            worksheet.merge_range(row, 3, row, 12, product.list_price, text_products)
            worksheet.merge_range(row, 13, row, 22, product.name, text_products)
            worksheet.merge_range(row, 23, row, 29, product.name, text_products)
            worksheet.merge_range(row, 30, row, 32, product.list_price, text_price)
            row += 1
            total_OE += product.list_price
        worksheet.merge_range(row, 26, row, 29, 'Total', text_price2)
        worksheet.merge_range(row, 30, row, 32, total_OE, text_price)
        worksheet.merge_range(row+1, 26, row+1, 29, 'TOTAL EGC', title_price)
        worksheet.merge_range(row+1, 30, row+1, 32, total_OE, text_price2)
        worksheet.set_row(row+2, 20)
        worksheet.merge_range(row+2, 1, row+2, 33, 'Reporte Diario de Caja', title_format)
        worksheet.set_row(row+3, 1)
        worksheet.merge_range(row+3, 2, row+3, 10, '', borderformat)
        worksheet.merge_range(row+4, 2, row+4, 17, 'Ingresos a Caja', title_header)
        worksheet.merge_range(row+5, 1, row+5, 11, 'Tipo Emitido', title_header)
        worksheet.merge_range(row+5, 12, row+5, 21, 'Valor', title_price)
        worksheet.set_row(row+6, 1)
        worksheet.merge_range(row+6, 1, row+6, 21, '', borderformat)

        worksheet.merge_range(row+7, 1, row+7, 11, 'Facturas Contado', text_products)
        worksheet.merge_range(row+7, 12, row+7, 21, total_fact_c, text_price)
        worksheet.merge_range(row+8, 1, row+8, 11, 'Facturas Crédito', text_products)
        worksheet.merge_range(row+8, 12, row+8, 21, total_fact_c2, text_price)
        #total ingresos a caja
        sumaIGC2 = total_fact_c + total_fact_c2
        worksheet.merge_range(row+9, 1, row+9, 11, 'Cobros a Clientes', text_products)
        worksheet.merge_range(row+9, 12, row+9, 21, product.list_price, text_price)
        sumaIGC2 += product.list_price
        worksheet.merge_range(row+10, 1, row+10, 11, 'Ingresos Banco', text_products)
        worksheet.merge_range(row+10, 12, row+10, 21, product.list_price, text_price)
        sumaIGC2 += product.list_price
        worksheet.merge_range(row+11, 1, row+11, 11, 'Otros Ingresos', text_products)
        worksheet.merge_range(row+11, 12, row+11, 21, product.list_price, text_price)
        sumaIGC2 += product.list_price
        worksheet.merge_range(row+12, 1, row+12, 11, 'Total ', title_price)
        worksheet.merge_range(row+12, 12, row+12, 21, sumaIGC2, text_price2)

        worksheet.merge_range(row+13, 2, row+13, 17, 'Egresos de Caja ', title_header)
        worksheet.merge_range(row+14, 2, row+14, 7, 'Tipo Emitido ', title_header)
        worksheet.merge_range(row+14, 10, row+14, 19, 'Valor', title_price)
        worksheet.set_row(row+15, 1)
        worksheet.merge_range(row+15, 2, row+15, 19, '', borderformat)
        worksheet.set_row(row+16, 1)
        worksheet.merge_range(row+17, 2, row+17, 8, 'OTROS EGRESOS(3)', text_products)
        worksheet.merge_range(row+17, 10, row+17, 18, total_OE,  text_price)
        worksheet.set_row(row+18, 1)
        worksheet.merge_range(row+19, 2, row+19, 8, 'Total:', title_price)
        worksheet.merge_range(row+19, 10, row+19, 18, total_OE, text_price2)
        worksheet.set_row(row+19, 1)
        worksheet.merge_range(row+20, 2, row+20, 17, 'Notas de credito ', title_header)
        worksheet.merge_range(row+21, 2, row+21, 7, 'Tipo Emitido ', title_header)
        worksheet.merge_range(row+21, 10, row+22, 19, 'Valor', title_price)
        worksheet.set_row(row+22, 1)
        worksheet.merge_range(row+22, 2, row+22, 19, '', borderformat)
        worksheet.set_row(row+23, 1)
        worksheet.merge_range(row+24, 2, row+24, 8, 'Notas de credito de', text_products)
        worksheet.merge_range(row+24, 10, row+24, 18, total_NC,  text_price)
        worksheet.set_row(row+25, 1)
        worksheet.merge_range(row+26, 2, row+26, 8, 'Total:', title_price)
        worksheet.merge_range(row+26, 10, row+26, 18, total_NC, text_price2)
        worksheet.set_row(row+27, 1)

        worksheet.merge_range(row+28, 2, row+28, 14, 'Formas de Pago General', title_header)
        worksheet.merge_range(row+29, 2, row+29, 4, 'Formas de Pago', title_header)
        worksheet.merge_range(row+29, 7, row+29, 15, 'Apertura', title_price)
        worksheet.merge_range(row+29, 17, row+29, 23, 'Valor Ingreso', title_price)
        worksheet.merge_range(row+29, 25, row+29, 27, 'Valor Egreso', title_price)
        worksheet.merge_range(row+29, 29, row+29, 31, 'Saldo', title_price)
        worksheet.set_row(row+30, 1)
        worksheet.merge_range(row+30, 2, row+30, 30, '', borderformat)

        row = row+31
        sumaToIn = 0
        sumaToEg = 0

        for product in products:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.merge_range(row, 2, row, 4, product.name, text_products)
            worksheet.merge_range(row, 7, row, 15, product.standard_price, text_price)
            worksheet.merge_range(row, 17, row, 23, product.list_price, text_price)
            worksheet.merge_range(row, 25, row, 27, product.standard_price, text_price)
            #valor = apertura + ingresos - egresos
            worksheet.merge_range(row, 29, row, 31, ((product.standard_price + product.list_price) - product.standard_price), text_price)
            row += 1
            sumaToIn += product.list_price
            sumaToEg += product.standard_price

        worksheet.merge_range(row, 7, row, 15, 'TOTALES', text_price2)
        #VALOR INGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 17, row, 23, sumaToIn, text_price2)
        #VALOR EGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 25, row, 28, sumaToEg, text_price2)
        worksheet.merge_range(row+1, 2, row+1, 20, 'Formas de Pago de Facturas Contado', title_header)
        worksheet.merge_range(row+2, 2, row+2, 4, 'Formas de Pago', title_header)
        worksheet.merge_range(row+2, 7, row+2, 15, 'Valor', title_price)
        worksheet.set_row(row+3, 1)
        worksheet.merge_range(row+3, 2, row+3, 15, '', borderformat)

        row = row + 4
        total_ef = 0

        for product in products:
            worksheet.set_row(row, 12)  # Establece la altura de la fila en 20 puntos
            worksheet.merge_range(row, 2, row, 4, product.name, text_products)
            #VALOR FORMAS DE PAGO
            worksheet.merge_range(row, 7, row, 15, product.list_price, text_price)
            row += 1
            total_ef += product.list_price
        worksheet.merge_range(row, 2, row, 3, 'Totales', text_price2)
        worksheet.merge_range(row, 7, row, 15, total_ef, text_price2)

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'Reporte Diario de Venta detalllado PORTETE CON FALTANTE.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
    def action_generate_xlsx_report3(self, products):
        # Crear un archivo XLSX en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Documento')
        worksheet.hide_gridlines(option=2)

        title_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "font_size": 14,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True
            })

        title_header = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            })

        title_header1 = workbook.add_format({
            "bold": True,
            "align": "left",
            "font_size": 10,
            "font_name": "SansSerif",
            "valign": "vcenter",
            "text_wrap": True,
            "underline": 1  # Agregar subrayado
            })

        title_price = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
            })

        text_price = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_price2 = workbook.add_format({
            'font_name': 'SansSerif',
            'bold': True,
            'font_size': 8,
            'align': 'right',
            'valign': 'top',
            'text_wrap': True
        })

        text_products = workbook.add_format({
            'font_name': 'SansSerif',
            'font_size': 8,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        borderformat = workbook.add_format({
            'text_wrap': True,
            'bottom': 2
        })

        worksheet.set_row(0, 25)
        worksheet.set_row(1, 25)
        worksheet.set_row(2, 1)
        worksheet.set_row(3, 20)
        worksheet.set_column('A:A', 4.5)
        worksheet.set_column('B:B', 0.1)
        worksheet.set_column('C:C', 11.6)
        worksheet.set_column('D:D', 1.5)
        worksheet.set_column('E:E', 0.8)

        worksheet.set_column('F:J', 0.1)
        worksheet.set_column('K:K', 0.5)
        worksheet.set_column('L:L', 4)
        worksheet.set_column('M:M', 0.8)
        worksheet.set_column('N:N', 4.5)
        worksheet.set_column('O:O', 0.1)
        worksheet.set_column('P:P', 4)
        worksheet.set_column('Q:Q', 0.1)
        worksheet.set_column('R:R', 0.1)
        worksheet.set_column('S:S', 1)
        worksheet.set_column('T:T', 0.5)
        worksheet.set_column('U:U', 4.5)
        worksheet.set_column('V:V', 0.1)
        worksheet.set_column('W:W', 12)
        worksheet.set_column('X:Y', 0.1)
        worksheet.set_column('Z:Z', 11)
        worksheet.set_column('AA:AA', 0.2)
        worksheet.set_column('AB:AB', 20)
        worksheet.set_column('AC:AC', 4.5)

        for row_buc in range(1, 20):
            worksheet.set_row(row_buc, 12)

        worksheet.merge_range('B1:AB1', 'Reporte  Diario de Caja ', title_format)
        worksheet.set_row(2, 1)
        worksheet.merge_range('C3:J3', '', borderformat)
        worksheet.merge_range('C4:P4', 'Ingresos a Caja', title_header)
        worksheet.merge_range('B5:K5', 'Tipo Emitido', title_header)
        worksheet.merge_range('L5:T5', 'Valor', title_header)
        worksheet.set_row(5, 1)
        worksheet.merge_range('B6:T6', '', borderformat)

        #recorrer las facturas pagadas al contado

        Fac_Contado = 0
        for product in products:
            Fac_Contado += product.list_price

        Fac_Credito = 0
        for product in products:
            Fac_Credito += product.list_price

        worksheet.merge_range('B7:K7', 'Facturas Contado', text_products)
        worksheet.merge_range('L7:T7', Fac_Contado, text_price)
        worksheet.merge_range('B8:K8', 'Facturas Crédito', text_products)
        worksheet.merge_range('L8:T8', Fac_Credito, text_price)
        worksheet.merge_range('B9:K9', 'Cobros a Clientes', text_products)
        worksheet.merge_range('L9:T9', product.list_price, text_price)
        worksheet.merge_range('B10:K10', 'Ingresos Banco', text_products)
        worksheet.merge_range('L10:T10', product.list_price, text_price)
        worksheet.merge_range('B11:K11', 'Otros Ingresos', text_products)
        worksheet.merge_range('L11:T11', product.list_price, text_price)
        worksheet.merge_range('B12:K12', 'Total ', title_price)
        sumaIG = Fac_Contado + Fac_Credito + product.list_price + product.list_price + product.list_price
        worksheet.merge_range('L12:T12', sumaIG, text_price2)

        worksheet.merge_range('C13:P13', 'Egresos de Caja ', title_header)
        worksheet.merge_range('C14:G14', 'Tipo Emitido ', title_header)
        worksheet.merge_range('J14:R14', 'Valor', title_price)
        worksheet.set_row(14, 1)
        worksheet.set_row(15, 1)
        worksheet.merge_range('C16:R16', '', borderformat)
        worksheet.merge_range('C17:H17', 'OTROS EGRESOS(3)', text_products)

        #RECORRER OTROS EGRESOS

        total_OE = 2
        for product in products:
            total_OE += product.list_price

        worksheet.merge_range('J17:Q17',  total_OE,  text_price)
        worksheet.set_row(17, 1)
        worksheet.set_row(18, 1)
        worksheet.merge_range('C20:H20', 'DEPOSITO BANCARIO(6)', text_products)

        #RECORRER EGRESO DEPOSITO BANCARIO
        total_EGB = 3
        for product in products:
            total_EGB += product.list_price

        worksheet.merge_range('J20:Q20',  total_EGB,  text_price)
        worksheet.set_row(20, 1)
        worksheet.merge_range('C22:H22', 'Total:', title_price)
        worksheet.merge_range('J22:Q22',  (total_OE + total_EGB),  text_price2)
        worksheet.set_row(22, 1)
        worksheet.merge_range('C24:M24', 'Formas de Pago General', title_header)
        worksheet.merge_range('C25:D25', 'Formas de Pago', title_header)
        worksheet.merge_range('G25:N25', 'Apertura', title_price)
        worksheet.merge_range('P25:U25', 'Valor Ingreso', title_price)
        worksheet.merge_range('W25:X25', 'Valor Egreso', title_price)
        worksheet.merge_range('Z25:AA25', 'Saldo', title_price)
        worksheet.set_row(25, 1)
        worksheet.merge_range('C26:Z26', '', borderformat)

        row = 27
        sumaToIn = 0
        sumaToEg = 0

        #FORMAS DE PAGO
        for product in products:
            worksheet.set_row(row, 12)
            worksheet.merge_range(row, 2, row, 4, product.name, text_products)
            worksheet.merge_range(row, 6, row, 13, product.standard_price, text_price)
            worksheet.merge_range(row, 15, row, 20, product.list_price, text_price)
            worksheet.write(row, 22, product.list_price, text_price)
            #valor = apertura + ingresos - egresos
            worksheet.merge_range(row, 25, row, 26, ((product.standard_price + product.list_price) - product.list_price), text_price)
            row += 1
            sumaToIn += product.list_price
            sumaToEg += product.list_price

        worksheet.merge_range(row, 6, row, 13, 'TOTALES', text_price2)
        #VALOR INGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 15, row, 20, sumaToIn, text_price2)
        #VALOR EGRESO FORMAS DE PAGO
        worksheet.merge_range(row, 22, row, 24, sumaToEg, text_price2)

        worksheet.merge_range(row+1, 2, row+1, 18, 'Formas de Pago de Facturas Contado', title_header)
        worksheet.merge_range(row+2, 2, row+2, 3, 'Formas de Pago', title_header)
        worksheet.merge_range(row+2, 6, row+2, 13, 'Valor', title_price)
        worksheet.set_row(row+3, 1)
        worksheet.merge_range(row+3, 2, row+3, 13, '', borderformat)

        row = row + 4
        total_ef = 0

        for product in products:  # PAGOS AL CONTADO
            worksheet.set_row(row, 12)
            worksheet.merge_range(row, 2, row, 4, product.name, text_products)
            #VALOR FORMAS DE PAGO
            worksheet.merge_range(row, 6, row, 13, product.list_price, text_price)
            row += 1
            total_ef += product.list_price
        worksheet.write(row, 2, 'TOTALES', text_price2)
        worksheet.merge_range(row, 6, row, 13, total_ef, text_price2)

        workbook.close()
        output.seek(0)

        # Crear un archivo adjunto
        attachment = self.env['ir.attachment'].create({
            'name': 'Reporte Diario de Venta Resumido.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
