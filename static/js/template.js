(function($) {
  'use strict';
  $(function() {
    var body = $('body');
    var contentWrapper = $('.content-wrapper');
    var scroller = $('.container-scroller');
    var footer = $('.footer');
    var sidebar = $('.sidebar');

    //Add active class to nav-link based on url dynamically
    //Active class can be hard coded directly in html file also as required

    function addActiveClass(element) {
      if (current === "") {
        //for root url
        if (element.attr('href').indexOf("index.html") !== -1) {
          element.parents('.nav-item').last().addClass('active');
          if (element.parents('.sub-menu').length) {
            element.closest('.collapse').addClass('show');
            element.addClass('active');
          }
        }
      } else {
        //for other url
        if (element.attr('href').indexOf(current) !== -1) {
          element.parents('.nav-item').last().addClass('active');
          if (element.parents('.sub-menu').length) {
            element.closest('.collapse').addClass('show');
            element.addClass('active');
          }
          if (element.parents('.submenu-item').length) {
            element.addClass('active');
          }
        }
      }
    }

    var current = location.pathname.split("/").slice(-1)[0].replace(/^\/|\/$/g, '');
    $('.nav li a', sidebar).each(function() {
      var $this = $(this);
      addActiveClass($this);
    })

    $('.horizontal-menu .nav li a').each(function() {
      var $this = $(this);
      addActiveClass($this);
    })

    //Close other submenu in sidebar on opening any

    sidebar.on('show.bs.collapse', '.collapse', function() {
      sidebar.find('.collapse.show').collapse('hide');
    });


    //Change sidebar and content-wrapper height
    applyStyles();

    function applyStyles() {
      //Applying perfect scrollbar
      if (!body.hasClass("rtl")) {
        if ($('.settings-panel .tab-content .tab-pane.scroll-wrapper').length) {
          const settingsPanelScroll = new PerfectScrollbar('.settings-panel .tab-content .tab-pane.scroll-wrapper');
        }
        if ($('.chats').length) {
          const chatsScroll = new PerfectScrollbar('.chats');
        }
        if (body.hasClass("sidebar-fixed")) {
          if($('#sidebar').length) {
            var fixedSidebarScroll = new PerfectScrollbar('#sidebar .nav');
          }
        }
      }
    }

    $('[data-toggle="minimize"]').on("click", function() {
      if ((body.hasClass('sidebar-toggle-display')) || (body.hasClass('sidebar-absolute'))) {
        body.toggleClass('sidebar-hidden');
      } else {
        body.toggleClass('sidebar-icon-only');
      }
    });

    //checkbox and radios
    $(".form-check label,.form-radio label").append('<i class="input-helper"></i>');

    //Horizontal menu in mobile
    $('[data-toggle="horizontal-menu-toggle"]').on("click", function() {
      $(".horizontal-menu .bottom-navbar").toggleClass("header-toggled");
    });
    // Horizontal menu navigation in mobile menu on click
    var navItemClicked = $('.horizontal-menu .page-navigation >.nav-item');
    navItemClicked.on("click", function(event) {
      if(window.matchMedia('(max-width: 991px)').matches) {
        if(!($(this).hasClass('show-submenu'))) {
          navItemClicked.removeClass('show-submenu');
        }
        $(this).toggleClass('show-submenu');
      }        
    })

    $(window).scroll(function() {
      if(window.matchMedia('(min-width: 992px)').matches) {
        var header = $('.horizontal-menu');
        if ($(window).scrollTop() >= 70) {
          $(header).addClass('fixed-on-scroll');
        } else {
          $(header).removeClass('fixed-on-scroll');
        }
      }
    });
  });


  $(document).ready(function() {
    var table = $('#myTable');
    var rowsPerPage = 10;
    var currentPage = 1;
    var totalRows = table.find('tbody tr:not(.no-data-found)').length;
    var totalPages = Math.max(1, Math.ceil(totalRows / rowsPerPage));

    function showPage(page) {
        table.find('tbody tr').hide();
        var startIndex = (page - 1) * rowsPerPage;
        var endIndex = startIndex + rowsPerPage;
        table.find('tbody tr').slice(startIndex, endIndex).show();
    }

    function updatePagination() {
        var paginationControls = $('#paginationControls');
        paginationControls.empty();
        var maxPageLinks = 5;
        var startPage = Math.max(1, currentPage - Math.floor(maxPageLinks / 2));
        var endPage = Math.min(totalPages, startPage + maxPageLinks - 1);

        if (totalRows > 0) {
            if (currentPage > 1) {
                paginationControls.append('<button id="firstPage">First</button>');
                paginationControls.append('<button id="prevPage">Previous</button>');
            }
            for (var i = startPage; i <= endPage; i++) {
                var pageButton = $('<button class="page">' + i + '</button>');
                if (i === currentPage) {
                    pageButton.addClass('active');
                }
                paginationControls.append(pageButton);
            }
            if (currentPage < totalPages) {
                paginationControls.append('<button id="nextPage">Next</button>');
                paginationControls.append('<button id="lastPage">Last</button>');
            }
        }

        // Calculate and update entries text here
        var startEntry = (currentPage - 1) * rowsPerPage + 1;
        var endEntry = Math.min(currentPage * rowsPerPage, totalRows);
        var entriesText = totalRows > 0
            ? 'Showing ' + startEntry + ' to ' + endEntry + ' of ' + totalRows + ' entries'
            : '';
        paginationControls.append('<div id="entriesInfo">' + entriesText + '</div');
    }

    showPage(currentPage);
    updatePagination();

    $('#search').on('keyup', function() {
        handleSearch();
    });

    $('#paginationControls').on('click', '#firstPage', function() {
        currentPage = 1;
        showPage(currentPage);
        updatePagination();
    });

    $('#paginationControls').on('click', '#lastPage', function() {
        currentPage = totalPages;
        showPage(currentPage);
        updatePagination();
    });

    $('#paginationControls').on('click', '#nextPage', function() {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
            updatePagination();
        }
    });

    $('#paginationControls').on('click', '#prevPage', function() {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
            updatePagination();
        }
    });

    $('#paginationControls').on('click', '.page', function() {
        var newPage = parseInt($(this).text());
        if (newPage !== currentPage) {
            currentPage = newPage;
            showPage(currentPage);
            updatePagination();
        }
    });

  function handleSearch() {
    var searchText = $('#search').val().toLowerCase();
    var visibleRows = table.find('tbody tr:not(.no-data-found)').filter(function() {
        var rowText = $(this).text().toLowerCase();
        return rowText.includes(searchText);
    });
    totalRows = visibleRows.length; // Update totalRows with the count of visible rows

    if (searchText === "") {
        showPage(1);
        updatePagination();
    } else {
        // Hide all rows first and then show the filtered rows
        table.find('tbody tr').hide();
        visibleRows.show();

        currentPage = 1; // Reset to page 1 after a search
                totalPages = Math.max(1, Math.ceil(totalRows / rowsPerPage));

        updatePagination();
    }
}
});



  // focus input when clicking on search icon
  $('#navbar-search-icon').click(function() {
    $("#navbar-search-input").focus();
  });


     document.addEventListener('DOMContentLoaded', function() {
     const forms = document.querySelectorAll('.needs-validation, .needs-password-validation');
    forms.forEach(form => {
        form.addEventListener(
            'submit',
            event => {
                if (!form.checkValidity()) {
                    event.preventDefault();   // Prevent submission if the form is not valid.
                    event.stopPropagation();  // Stop the event from propagating further.
                }

                // Password matching validation
                if (form.classList.contains('needs-password-validation')) {
                    const passwordField = form.querySelector('#password');
                    const confirmPasswordField = form.querySelector('#confirmPassword');
                    if (passwordField.value !== confirmPasswordField.value) {
                        event.preventDefault(); // Prevent form submission
                        event.stopPropagation(); // Stop the event from propagating further.
                        confirmPasswordField.setCustomValidity("Passwords do not match.");
                    } else {
                        confirmPasswordField.setCustomValidity("");
                    }
                }

                form.classList.add('was-validated');
            },
            false
        );
    });
    });

  document.getElementById('backButton').addEventListener('click', function() {
    window.history.back();
});
})(jQuery);