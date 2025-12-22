$(function() {
  "use strict";

  //------- Parallax -------//
  if(typeof skrollr !== 'undefined') {
    skrollr.init({
      forceHeight: false
    });
  }

  //------- Active Nice Select --------//
  if(typeof $.fn.niceSelect !== 'undefined') {
    $('select').niceSelect();
  } else {
    // Fallback: try again after a short delay if plugin not immediately available
    setTimeout(function() {
      if(typeof $.fn.niceSelect !== 'undefined') {
        $('select').niceSelect();
      }
    }, 500);
  }

  //------- hero carousel -------//
  if(typeof $.fn.owlCarousel !== 'undefined' && $(".hero-carousel").length > 0) {
    $(".hero-carousel").owlCarousel({
      items:3,
      margin: 10,
      autoplay:false,
      autoplayTimeout: 5000,
      loop:true,
      nav:false,
      dots:false,
      responsive:{
        0:{
          items:1
        },
        600:{
          items: 2
        },
        810:{
          items:3
        }
      }
    });
  }

  //------- Best Seller Carousel -------//
  if(typeof $.fn.owlCarousel !== 'undefined' && $('#bestSellerCarousel').length > 0){
    $('#bestSellerCarousel').owlCarousel({
      loop:true,
      margin:30,
      nav:true,
      navText: ["<i class='ti-arrow-left'></i>","<i class='ti-arrow-right'></i>"],
      dots: false,
      responsive:{
        0:{
          items:1
        },
        600:{
          items: 2
        },
        900:{
          items:3
        },
        1130:{
          items:4
        }
      }
    })
  }

  //------- single product area carousel -------//
  if(typeof $.fn.owlCarousel !== 'undefined' && $(".s_Product_carousel").length > 0) {
    $(".s_Product_carousel").owlCarousel({
      items:1,
      autoplay:false,
      autoplayTimeout: 5000,
      loop:true,
      nav:false,
      dots:false
    });
  }

  //------- mailchimp --------//  
	function mailChimp() {
		$('#mc_embed_signup').find('form').ajaxChimp();
	}
  mailChimp();
  
  //------- fixed navbar --------//  
  $(window).scroll(function(){
    var sticky = $('.header_area'),
    scroll = $(window).scrollTop();

    if (scroll >= 100) sticky.addClass('fixed');
    else sticky.removeClass('fixed');
  });

  //------- Price Range slider -------//
  if(document.getElementById("price-range")){
  
    var nonLinearSlider = document.getElementById('price-range');
    
    noUiSlider.create(nonLinearSlider, {
        connect: true,
        behaviour: 'tap',
        start: [ 500, 4000 ],
        range: {
            // Starting at 500, step the value by 500,
            // until 4000 is reached. From there, step by 1000.
            'min': [ 0 ],
            '10%': [ 500, 500 ],
            '50%': [ 4000, 1000 ],
            'max': [ 10000 ]
        }
    });
  
  
    var nodes = [
        document.getElementById('lower-value'), // 0
        document.getElementById('upper-value')  // 1
    ];
  
    // Display the slider value and how far the handle moved
    // from the left edge of the slider.
    nonLinearSlider.noUiSlider.on('update', function ( values, handle, unencoded, isTap, positions ) {
        nodes[handle].innerHTML = values[handle];
    });
  
  }
  
});


