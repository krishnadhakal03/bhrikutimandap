$(function() {
  "use strict";

  //------- Parallax -------//
  if(typeof skrollr !== 'undefined') {
    skrollr.init({
      forceHeight: false
    });
  }

  //------- Active Nice Select --------//
  if($.fn.niceSelect) {
    $('select').niceSelect();
  }

  //------- Hero Carousel -------//
  if($(".hero-carousel").length) {
    $(".hero-carousel").owlCarousel({
      items: 3,
      margin: 15,
      autoplay: false,
      autoplayTimeout: 5000,
      loop: true,
      nav: false,
      dots: false,
      responsive: {
        0: {
          items: 1
        },
        600: {
          items: 2
        },
        810: {
          items: 3
        }
      }
    });
  }

  //------- Best Seller Carousel -------//
  if($('#bestSellerCarousel').length) {
    $('#bestSellerCarousel').owlCarousel({
      loop: true,
      margin: 30,
      nav: true,
      navText: ["<i class='ti-arrow-left'></i>", "<i class='ti-arrow-right'></i>"],
      dots: false,
      responsive: {
        0: {
          items: 1
        },
        600: {
          items: 2
        },
        900: {
          items: 3
        },
        1130: {
          items: 4
        }
      }
    });
  }

  //------- Single Product Carousel -------//
  if($(".s_Product_carousel").length) {
    $(".s_Product_carousel").owlCarousel({
      items: 1,
      autoplay: false,
      autoplayTimeout: 5000,
      loop: true,
      nav: false,
      dots: false
    });
  }

  //------- MailChimp --------//  
  function mailChimp() {
    if($('#mc_embed_signup').find('form').length && $.fn.ajaxChimp) {
      $('#mc_embed_signup').find('form').ajaxChimp();
    }
  }
  mailChimp();
  
  //------- Fixed Navbar on Scroll --------//  
  $(window).scroll(function() {
    var sticky = $('.header_area'),
        scroll = $(window).scrollTop();

    if (scroll >= 100) {
      sticky.addClass('fixed');
    } else {
      sticky.removeClass('fixed');
    }
  });

  //------- Price Range Slider -------//
  if(document.getElementById("price-range") && typeof noUiSlider !== 'undefined') {
    var nonLinearSlider = document.getElementById('price-range');
    
    noUiSlider.create(nonLinearSlider, {
      connect: true,
      behaviour: 'tap',
      start: [500, 4000],
      range: {
        'min': [0],
        '10%': [500, 500],
        '50%': [4000, 1000],
        'max': [10000]
      }
    });

    var lowerValue = document.getElementById('lower-value');
    var upperValue = document.getElementById('upper-value');

    if(lowerValue && upperValue) {
      nonLinearSlider.noUiSlider.on('update', function(values, handle) {
        if(handle === 0) {
          lowerValue.innerHTML = Math.round(values[0]);
        } else {
          upperValue.innerHTML = Math.round(values[1]);
        }
      });
    }
  }

  //------- Image Error Handling -------//
  $('img').on('error', function() {
    // Create placeholder SVG for failed images
    var fallbackSvg = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 200%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22 font-family=%22Arial%22 font-size=%2214%22%3EImage Not Found%3C/text%3E%3C/svg%3E';
    $(this).attr('src', fallbackSvg).css('opacity', '0.5');
  });

  //------- Smooth Scrolling for Anchor Links -------//
  $('a[href^="#"]').on('click', function(e) {
    e.preventDefault();
    var target = $(this.getAttribute('href'));
    if(target.length) {
      $('html, body').stop().animate({
        scrollTop: target.offset().top - 80
      }, 1000);
    }
  });

  //------- Add Loading State to Forms -------//
  $('form').on('submit', function() {
    var submitBtn = $(this).find('button[type="submit"]');
    if(submitBtn.length) {
      submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processing...');
    }
  });

  //------- Tooltip Initialization -------//
  if($.fn.tooltip) {
    $('[data-toggle="tooltip"]').tooltip();
  }

});

// Fallback for console.log to prevent errors
if(typeof console === 'undefined') {
  window.console = {
    log: function() {},
    error: function() {},
    warn: function() {}
  };
}
