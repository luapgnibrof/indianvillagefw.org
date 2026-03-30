(function() {
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.main-nav');

  toggle.addEventListener('click', function() {
    var expanded = nav.classList.toggle('active');
    toggle.setAttribute('aria-expanded', expanded);
  });

  // Prevent parent dropdown links (#) from scrolling to top;
  // on mobile, toggle the submenu on click instead.
  document.querySelectorAll('.has-children > a[href="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var submenu = link.nextElementSibling;
      if (submenu) {
        var isOpen = submenu.style.display === 'block';
        submenu.style.display = isOpen ? '' : 'block';
        link.setAttribute('aria-expanded', !isOpen);
      }
    });
  });
})();
