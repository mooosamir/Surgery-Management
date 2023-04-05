odoo.define('integrate_tour_web.package', function(require){
    'use strict';

    var Animation = require('website.content.snippets.animation');
    require('web.dom_ready');
    var ajax = require('web.ajax');
    

    
    if (window.location.pathname === '/package') {
        miFuncion();
    }

    var allPrice = $( ".allPrice" )
    allPrice.on('click',function(e) {

        $("#precioH").val($(this).attr('data-isotope-option'))
        miFuncion();

      });

      $(".ubica").on('click',function(e){
        $("#locationH").val($(this).attr('data-isotope-option'))
        miFuncion();

      })

      $(".hoteles").on('click',function(e){
        $("#hotelH").val($(this).attr('data-isotope-option'))
        miFuncion();

      })
      $('#load_more_button').on('click', function() {
        miFuncion(1);
    });
    
    
    function miFuncion(limit = 0) {
        
        let dataseto = {} 
        if($("#precioH").val() != ""){
            dataseto['order']= $("#precioH").val()
        }
        if($("#locationH").val() != ""){
            dataseto['location']= $("#locationH").val()
        }
        if($("#hotelH").val() != ""){
            dataseto['hotel']= $("#hotelH").val()
        }
        console.log(dataseto)

        if(!limit){
           
            dataseto['limit'] = 10; // número de registros por página

        }else{
            dataseto['limit'] = parseInt($("#paginado").val()) 
        }
        

        dataseto['offset'] = 0; // valor inicial del offset
        

        var self = this;
        ajax.jsonRpc('/get_package', 'call', {
            method: 'get',
            args: [dataseto],
        })
        .then(function (data) {
            if(data){
                $("#insert").empty()
                $.each(data, function( index, value ) {
                    
                    var f = new Date().toISOString().split('T')[0]
                    console.log(value.f_d_hasta > f)
                 $("#insert").append(`

                 <div class="offers_item rating_4" >
                    <div class="row">
                        <div class="col-lg-1 temp_col"></div>
                        <div class="col-lg-3 col-1680-4">
                            <div class="offers_image_container">
                                <!-- Image by https://unsplash.com/@kensuarez -->
                                <div class="offers_image_background"  style="background-image: url(data:image/png;base64,${value.image});max-width: 500; min-width: 400; min-height: 400; max-height: 500;"></div>
                                
                                <div class="offer_name"><a href="#">${value.name}</a></div> 
                            </div>
                        </div>
                        <div class="col-lg-8">
                            <div class="offers_content">
                                 <div class="offers_price">${value.precio_rate} ${value.currency.symbol}
                                 
                                 <span>${value.total_days >1? value.total_days+" Dias" : value.total_days+" Dia" }</span>
                                  <span>${value.total_night ? value.total_night == 1 ? value.total_night+" Noche"  : value.total_night+" Noches" : ""} </span></div>
                                <p class="offers_text" style=" text-align: justify; ">${value.note}</p> 
                                 
                                
                                <div class="button book_button"><a href="/package/${value.id}/">Mas Detalles<span></span><span></span><span></span></a></div>
                                <div class="offer_reviews">
                                ${value.descuentos_web && value.f_d_hasta > f? `
                                <div class="offer_reviews_content">
                                        <div class="offer_reviews_title" align="right">Descuentos</div>
                                        <div class="offer_reviews_subtitle">Desde ${value.f_d_desde} <span> Hasta</span>  ${value.f_d_hasta}</div>
                                    </div>
                                    <div class="offer_reviews_rating text-center">${value.descuentos_web? value.descuentos_web: ""} %</div>
                                
                                `: ""}
                                    
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                 </br>
                 `);
                
                 // Actualizar el offset para la próxima página
                
            });

            dataseto.limit += 10;
            $("#paginado").val(dataseto.limit)
            }
        });
    }

    

   
});

