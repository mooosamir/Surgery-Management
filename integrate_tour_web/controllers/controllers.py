# # -*- coding: utf-8 -*-
# from odoo import http, fields
# from odoo.http import request
from posixpath import supports_unicode_filenames
import re
from unicodedata import category
from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime ,timedelta

class main_package(http.Controller):

    @http.route('/package', auth="public", method=['GET'], csrf=False , website=True)
    def get_main_package(self):
        try:
            package = request.env['tour.package'].sudo().search(
                [('website_published', '=', True)],
                order='create_date asc', limit=8)
            localizacion = request.env['tour.location'].sudo().search([],order='name')
            hotel = request.env['tour.hotel'].sudo().search([],order='name')
            values = {
                'main_package': package,
                'localizacion': localizacion,
                'hotel':hotel,
            }
            
            response = http.Response(template='integrate_tour_web.package_views_1',
                                    qcontext=values)
            return response.render()
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json;charset=utf-8', status=505)



    @http.route('/get_package',  type="json", auth="public", method=['GET'], csrf=False , website=True)
    def object_get_package(self,args):
        
        try:
            
            con = [('website_published', '=', True)]
            m=[]
            res={}
            localizacion_ist=[]
            hotel_ist=[]
            
            if 'order' not in args[0]:
                args[0]['order']='create_date asc'
                

            if 'location' in args[0]:
                con.append(('location_ids',"=", int(args[0]['location'])))

            if 'hotel' in args[0]:
                con.append(('days_ids.hotel_id',"=", int(args[0]['hotel'])))
            print(args[0],con)
            package = request.env['tour.package'].sudo().search(con,order= args[0]['order'], offset=int(args[0]['offset']), limit=int(args[0]['limit']))
            print(package)
           
            for items in package:
                currency_list = {}
                for currency in items.currency:
                    currency_list['currency']= currency.name
                    currency_list['symbol']= currency.symbol

                facilities_list={}
                for facilities in items.facilities_ids:
                    facilities_list['name'] = facilities.name

                days_list={}
                for days in items.days_ids:
                    days_list['day'] =  days.day
                    days_list['hotel_id'] = days.hotel_id.name
                    days_list['night_stay'] = days.night_stay
                    days_list['location_id'] = days.location_id.name
                
                location_list ={}
                for location in items.location_ids:
                    location_list['name'] = location.name
                    location_list['longitude'] = location.longitude
                    location_list['latitude'] = location.latitude
                    location_list['city'] = location.city
                    location_list['country'] = location.country_id.name
                    location_list['state_id'] = location.state_id.name
                
                    
                values = {
                    'id': items.id,
                    'name': items.name,
                    'price': items.price,
                    'total_days' : items.total_days,
                    'total_night':items.total_night,
                    'image' : items.image,
                    'website_published':items.website_published,
                    'season': items.season,
                    'package_seq':items.package_seq,
                    'type':items.type,
                    'location':location_list,
                    'days':days_list,
                    'currency':currency_list,
                    'tour_type':items.tour_type,
                    'facilities':facilities_list,
                    'on_cancellation':items.on_cancellation,
                    'on_date_change':items.on_date_change,
                    'title_term_condition':items.title_term_condition,
                    'term_condition':items.term_condition,
                    'inclusion':items.inclusion,
                    'exclusion':items.exclusion,
                    'note':items.note,
                    'payment':items.payment,
                    'descuentos_web' : items.descuentos_web,
                    'f_d_desde': items.f_d_desde,
                    'f_d_hasta': items.f_d_hasta,
                    'precio_rate':items.precio_rate
                }
                m.append(values)
            # print(m)
            return m
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json;charset=utf-8', status=505)
            
        



    @http.route('/package/<model("tour.package"):obj>',  type='http', auth="public", website=True, sitemap=False)
    # @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=False)
    def object(self, obj, **kw):

        if request.session.uid:
            # El usuario ha iniciado sesión, mostrar contenido específico
            try:
                datos = obj.read()[0]
                
                

                response = http.Response(template='integrate_tour_web.package_detalles', qcontext={'datos': obj.sudo(),'today': (datetime.now().strftime('%Y-%m-%d')<= obj.sudo().f_d_hasta.strftime('%Y-%m-%d'))})
                return response.render()
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), content_type='application/json;charset=utf-8', status=505)
        else:
            # El usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
            return http.request.redirect('/web/login?redirect=/package')
        
        


    @http.route('/validate_reserva', type='json', auth='user')
    def guardar_cliente(self, **post):
        # obtener los datos enviados por el formulario
        cedula_pasaporte = post.get('cedula_pasaporte')
        nombre = post.get('nombre')
        email = post.get('email')
        telefono = post.get('telefono')
        term_comd = post.get('term_comd')
        cantidad = int(post.get('cantidad'))

        fecha_formulario = datetime.strptime(post.get('fechaalta'), '%Y-%m-%d')
        fecha_formulario += timedelta(days=1)
        print(fecha_formulario , datetime.now())
        print(fecha_formulario < datetime.now())

        if fecha_formulario <= datetime.now():
             return {'success': False , 'msj':'No se puede realizar la reserva con fecha anterior a Mañana'}

        if term_comd == False:
            return {'success': False , 'msj':'Debe continuar con los terminos y condiciones para continuar con la reserva'}
        

        cliente = request.env['res.partner'].sudo().search([('email', '=', email)])
        if not cliente:
            return {'success': False , 'msj':'no se pudo validar los datos de seccion'}
        
        if cliente:
            
            for c in cliente:
                if c.vat != cedula_pasaporte:
                    return {'success': False , 'msj': 'Cedula o pasaporte incorrectos'}

                if c.name != nombre:
                    c.write({
                        'name': nombre,
                        
                    })
                if c.phone != telefono:
                     c.write({
                        'phone': telefono,   
                    })

            result= self.calculaCantidad(post.get('id_pck_m1'),cantidad) 

            return {'success': True, 'data' : result}



    def calculaCantidad(self,id_p,cantidad):
        package = request.env['tour.package'].sudo().search([('id', '=', id_p)])

        precio_unidad = package.price
        descuento = package.descuentos_web
        descuento_unidad = (precio_unidad * (descuento/100))
        precio_unidad_con_d = precio_unidad - descuento_unidad 
        precio_neto_sin_d = package.price * cantidad
        descuento_neto = descuento_unidad * cantidad
        precio_total_sin_d = precio_unidad * cantidad
        precio_total_con_d = precio_unidad_con_d * cantidad
        precio_unidad_USD= package.precio_rate
        descuento_USD= package.descuentos_web
        descuento_unidad_USD= (precio_unidad_USD * (descuento/100))
        precio_unidad_con_d_USD= precio_unidad_USD-descuento_unidad_USD
        precio_neto_sin_d_USD= package.precio_rate * cantidad
        descuento_neto_USD= descuento_unidad_USD * cantidad
        precio_total_sin_d_USD= package.precio_rate * cantidad
        precio_total_con_d_USD= precio_unidad_con_d_USD * cantidad

        return {
            'precio_unidad':precio_unidad,
            'descuento':descuento,
            'descuento_unidad':descuento_unidad,
            'precio_unidad_con_d':precio_unidad_con_d,
            'precio_neto_sin_d':precio_neto_sin_d,
            'descuento_neto':descuento_neto,
            'precio_total_sin_d':precio_total_sin_d,
            'precio_total_con_d':precio_total_con_d,
            'cantidad':cantidad,


            'precio_unidad_USD':precio_unidad_USD,
            'descuento_USD':descuento_USD,
            'descuento_unidad_USD':descuento_unidad_USD,
            'precio_unidad_con_d_USD':precio_unidad_con_d_USD,
            'precio_neto_sin_d_USD':precio_neto_sin_d_USD,
            'descuento_neto_USD':descuento_neto_USD,
            'precio_total_sin_d_USD':precio_total_sin_d_USD,
            'precio_total_con_d_USD':precio_total_con_d_USD,
        }
        






    @http.route('/Reservar', type='json', auth='user')
    def Reserva(self, **post):

        cedula_pasaporte = post.get('cedula_pasaporte')
        nombre = post.get('nombre')
        email = post.get('email')
        telefono = post.get('telefono')
        term_comd = post.get('term_comd')
        cantidad = int(post.get('cantidad'))
        user = request.env.user
        package = request.env['tour.package'].sudo().search([('id', '=', post.get('id_pck_m1'))])
        cliente = request.env['res.partner'].sudo().search([('email', '=', email),('id','=',user.partner_id.id)])
        
        if not package:
            return {'success': False , 'msj':'En estos momentos no podemos Validar su solicitud por favor intentelo mas tardes 01'}

        if not cliente:
            return {'success': False , 'msj':'no se pudo validar los datos de seccion'}

        tour_booking_model = http.request.env['tour.booking']
        new_booking = tour_booking_model.create({
            'customer_id': cliente.id, # Aquí debes indicar el ID del cliente correspondiente
            'package_id': package.id, # Aquí debes indicar el ID del paquete correspondiente
            'no_of_people': cantidad,
            'discount': 'offer',
            'discount_percentage': package.descuentos_web,
            'booking_time': post.get('fechaalta')
            
        })
        print(new_booking)

        if not new_booking:
            return {'success': False , 'msj':'En estos momentos no podemos Validar su solicitud por favor intentelo mas tarde 02'}
        else:
            return {'success': True , 'msj':'¡Opereracion exitosa!. Pronto Nuestro equipo se estara contactando con usted para culminar la reserva'}
        #     # si el cliente no existe, crear uno nuevo
        #     request.env['res.partner'].sudo().create({
        #         'name': nombre,
        #         'email': email,
        #         'phone': telefono,
        #         'customer': True,
        #     })
        #     return {'success': True}
