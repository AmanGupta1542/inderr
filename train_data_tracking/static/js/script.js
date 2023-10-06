// Adding dynamic active class in navbar
$(document).ready(function () {
    var url = window.location.href;
    // $('ul.navbar-nav a[href="'+url+'"]').addClass('active');
    console.log('running');
    $('ul.menu-inner a').filter(function() {
        if(this.href == url){
            $(this).parent().addClass('active');
            console.log($(this).parent().parent().parent().addClass('open active'));
            // $(this).parent().parent('li').addClass('open');
        }
         return this.href == url;
    });
  });
