# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class TourBooking(models.Model):
    _name = 'tour.booking'
    _description = 'Details About Tour Booking'
    _rec_name = 'book_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    book_seq = fields.Char(string='Secuencia', required=True, readonly=True, default=lambda self: ('Nuevo'))
    customer_id = fields.Many2one('res.partner', string='Cliente')
    package_id = fields.Many2one('tour.package', string='Paquete')
    package_type = fields.Selection(related='package_id.tour_type', string='Tipo de paquete')
    stage = fields.Selection([('draft', 'Borrador'),
                            ('confirm', 'Confirmado'),
                            ('cancel', 'Cancelado')], string='Etapa', default='borrador', readonly=1)
    booking_time = fields.Datetime(string='Hora de reserva', default=fields.Datetime.now)
    start_datetime = fields.Datetime(string='Inicio del tour')
    end_datetime = fields.Datetime(string='Fin del tour', compute='_compute_end_datetime')
    total_days = fields.Integer(related='package_id.total_days', string='Días totales')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    no_of_people = fields.Integer(string='No. de personas')
    tour_cost = fields.Monetary(string='Monto', compute='_compute_tour_cost')
    discount = fields.Selection([('fix', 'Precio fijo'),
                                ('offer', 'Oferta(%)')],
                                string='Descuento', default='precio fijo')
    discount_percentage = fields.Integer(string='Oferta(%)')
    final_cost = fields.Monetary(string='Monto total', compute='_compute_final_cost')
    invoice_id = fields.Many2one('account.move', string='Factura', readonly=True)
    is_any_child = fields.Boolean(string='¿Hay niños?')
    no_of_child = fields.Integer(string='No. de niños')
    child_cost = fields.Monetary(string='Cargos/Niño')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False)

    # Insurance
    insurance_number = fields.Char(string='Número de póliza')
    insurance_description = fields.Text(string='Descripción')
    insurance_price = fields.Monetary(string='Costo')
    insurance_term = fields.Text(string='Términos y condiciones')
    insurance_document = fields.Binary(string='Documento')
    file_name = fields.Char(string='Nombre de archivo')

    # Transporte
    driver_name = fields.Char(string='Nombre del conductor')
    vehicle_no = fields.Char(string='Número de vehículo')
    driver_phone_no = fields.Char(string='Número de teléfono del conductor')
    vehicle_model = fields.Char(string='Modelo')

    # Preferencias
    preference_ids = fields.One2many('extra.facilities', 'booking_id', string='Preferencias')
    total_charges = fields.Monetary(string='Costo total', compute='_compute_total_charge')

    # Vuelo
    flight_ids = fields.One2many('tour.flight', 'booking_id', string='Vuelos')
    flight_total_charge = fields.Monetary(string='Carga total', compute='_compute_flight_total_charge')

    # Documentos de visa
    documents_ids = fields.One2many('visa.document', 'booking_id', string='Documentos')


    @api.depends('preference_ids')
    def _compute_total_charge(self):
        for rec in self:
            if rec.preference_ids:
                price = 0.0
                for data in rec.preference_ids:
                    price = price + data.charge
                    rec.total_charges = price
            else:
                rec.total_charges = 0.0

    @api.depends('flight_ids')
    def _compute_flight_total_charge(self):
        for rec in self:
            if rec.flight_ids:
                price = 0.0
                for data in rec.flight_ids:
                    price = price + data.price
                    rec.flight_total_charge = price
            else:
                rec.flight_total_charge = 0.0

    @api.depends('no_of_people', 'package_id')
    def _compute_tour_cost(self):
        for rec in self:
            if rec.package_id:
                rec.tour_cost = rec.no_of_people * rec.package_id.price
            else:
                rec.tour_cost = 0.0

    @api.depends('tour_cost', 'discount_percentage')
    def _compute_final_cost(self):
        for rec in self:
            if rec.is_any_child:
                total = rec.no_of_child * rec.child_cost
                if rec.discount == 'fix':
                    rec.final_cost = rec.tour_cost + total
                else:
                    rec.final_cost = rec.tour_cost + total - ((rec.discount_percentage * (rec.tour_cost + total)) / 100)
            else:
                if rec.discount == 'fix':
                    rec.final_cost = rec.tour_cost
                else:
                    rec.final_cost = rec.tour_cost - ((rec.discount_percentage * rec.tour_cost) / 100)

    @api.model
    def create(self, vals):
        if vals.get('book_seq', ('New')) == ('New'):
            vals['book_seq'] = self.env['ir.sequence'].next_by_code(
                'tour.booking') or ('New')
        res = super(TourBooking, self).create(vals)
        return res

    @api.depends('start_datetime', 'total_days')
    def _compute_end_datetime(self):
        end_datetime = fields.Datetime.now()
        for rec in self:
            if rec['start_datetime']:
                rec['end_datetime'] = rec['start_datetime'] + datetime.timedelta(days=rec['total_days'])
            else:
                rec['end_datetime'] = end_datetime
        return True

    def action_crete_invoice(self):
        self.stage = 'confirm'
        for rec in self:
            final = ''
            record = ''
            flight_final = ''
            flight_record = ''
            for data in rec.preference_ids:
                description = data.title
                record = record + "{} - {} - {}{}, \n".format(data.category.capitalize(), description, data.charge,
                                                              self.currency_id.symbol)
            final = final + record
            for flight in rec.flight_ids:
                name = flight.name
                flight_record = flight_record + "{} - {}, \n".format(name, flight.pnr)
            flight_final = flight_final + flight_record
            invoice_lines = []
            if rec.package_id:
                package_record = {
                    'product_id': self.env.ref('tk_tour_management.tour_product_1').id,
                    'name': self.package_id.name + ' - ' + str(self.no_of_people) + ' People',
                    'quantity': 1,
                    'price_unit': self.final_cost
                }
                invoice_lines.append((0, 0, package_record))

            if rec.insurance_number:
                insurance_record = {
                    'product_id': self.env.ref('tk_tour_management.tour_product_2').id,
                    'name': 'Policy no . ' + self.insurance_number,
                    'quantity': 1,
                    'price_unit': self.insurance_price
                }
                invoice_lines.append((0, 0, insurance_record))

            if rec.preference_ids:
                addons_record = {
                    'product_id': self.env.ref('tk_tour_management.tour_product_3').id,
                    'name': final,
                    'quantity': 1,
                    'price_unit': self.total_charges
                }
                invoice_lines.append((0, 0, addons_record))

            if rec.flight_ids:
                flight_record = {
                    'product_id': self.env.ref('tk_tour_management.tour_product_4').id,
                    'name': flight_final,
                    'quantity': 1,
                    'price_unit': self.flight_total_charge
                }
                invoice_lines.append((0, 0, flight_record))

        data = {
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.date.today(),
            'invoice_line_ids': invoice_lines
        }
        if invoice_lines:
            invoice_id = self.env['account.move'].sudo().create(data)
            invoice_id.action_post()
            self.invoice_id = invoice_id.id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'res_model': 'account.move',
                'res_id': invoice_id.id,
                'view_mode': 'form,tree',
                'target': 'current'
            }

    def action_cancel(self):
        for rec in self:
            rec.stage = 'cancel'

    @api.model
    def get_tour_stats(self):
        total_booking = self.env['tour.booking'].sudo().search_count([])
        book_draft = self.env['tour.booking'].sudo().search_count([('stage', '=', 'draft')])
        book_confirm = self.env['tour.booking'].sudo().search_count([('stage', '=', 'confirm')])
        package_lead = self.env['crm.lead'].sudo().search_count([('type', '=', 'lead')])
        total_package = self.env['tour.package'].sudo().search_count([])
        domestic_packages = self.env['tour.package'].sudo().search_count([('tour_type', '=', 'domestic')])
        international_packages = self.env['tour.package'].sudo().search_count([('tour_type', '=', 'international')])

        data = {
            'book_draft': book_draft,
            'book_confirm': book_confirm,
            'total_booking': total_booking,
            'package_lead': package_lead,
            'domestic_packages': domestic_packages,
            'international_packages': international_packages,
            'total_package': total_package
        }
        return data


class ExtraFacilities(models.Model):
    _name = 'extra.facilities'
    _description = 'Extra Facilities While Booking'

    category = fields.Selection([('destination', 'Destinos'),
                             ('hotel', 'Hotel'),
                             ('transportation', 'Transporte'),
                             ('extra_service', 'Servicios Extra')],
                            string='Categoría')
    title = fields.Char(string='Descripción')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    charge = fields.Monetary(string='Costo')
    booking_id = fields.Many2one('tour.booking', string='Reserva Nro.')


class TourFlight(models.Model):
    _name = 'tour.flight'
    _description = 'Details related To Flight'

    name = fields.Char(string='Nombre')
    pnr = fields.Char(string='PNR No.')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    price = fields.Monetary(string='Precio')
    booking_id = fields.Many2one('tour.booking', string='Id de Reserva')
    flight_start = fields.Datetime(string='Hora de Salida')
    flight_end = fields.Datetime(string='Hora de Llegada')
    source_location = fields.Char(string='Ubicación de Origen')
    destination_location = fields.Char(string='Ubicación de Destino')


class VisaDocuments(models.Model):
    _name = 'visa.document'
    _description = 'Document For International Packages'

    name = fields.Char(string='Nombre')
    expiry_date = fields.Date(string='Fecha de Vencimiento')
    document_ids = fields.Many2many('document.list', string='Documentos')
    booking_id = fields.Many2one('tour.booking', string='ID de Reserva')
    color = fields.Integer(string='Color')


class DocumentList(models.Model):
    _name = 'document.list'
    _description = 'List Of Document'

    name = fields.Char('Documento')
    color = fields.Integer(string='Color')
