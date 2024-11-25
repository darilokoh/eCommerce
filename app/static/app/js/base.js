// Espera a que se cargue el DOM
document.addEventListener("DOMContentLoaded", function () {
  // Obtiene el elemento con el ID 'logout-link'
  var logoutLink = document.getElementById("logout-link");

  // Verifica si 'logoutLink' existe en la página
  if (!logoutLink) {
    return; // Salir si no existe
  }

  // Define una variable para indicar si el usuario ha iniciado sesión o no
  var isAuthenticated = false;

  // Busca el elemento con el ID 'is-authenticated' y verifica si está presente en la página
  var isAuthenticatedElement = document.getElementById("is-authenticated");
  if (isAuthenticatedElement) {
    // Si el elemento está presente, actualiza el valor de la variable isAuthenticated
    isAuthenticated = isAuthenticatedElement.value === "True";
  }

  // Verifica si el usuario ha iniciado sesión
  if (isAuthenticated) {
    // Agrega un event listener al enlace de cerrar sesión
    logoutLink.addEventListener("click", function (event) {
      event.preventDefault(); // Evita que el enlace se siga automáticamente
      Swal.fire({
        title: "¿Estás seguro de que quieres cerrar sesión?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, cerrar sesión",
        cancelButtonText: "Cancelar",
        reverseButtons: true,
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.href = event.target.href;
        }
      });
    });
  }
});


const cartToggle = document.getElementById("cart-toggle");
const cartContainer = document.getElementById("cart");
const cartCloseButton = document.getElementById("cart-close");
let isCartVisible = false;

cartToggle.addEventListener("click", () => {
  toggleCartVisibility();
});

cartCloseButton.addEventListener("click", () => {
  toggleCartVisibility();
});

window.addEventListener("scroll", () => {
  if (isCartVisible) {
    toggleCartVisibility();
  }
});

document.addEventListener("click", (event) => {
  const target = event.target;

  if (
    isCartVisible &&
    target !== cartToggle &&
    target !== cartContainer &&
    !cartContainer.contains(target)
  ) {
    toggleCartVisibility();
  }
});

function toggleCartVisibility() {
  if (!isCartVisible) {
    cartContainer.classList.remove('hide');
    cartContainer.classList.add('show');
    isCartVisible = true;
  } else {
    cartContainer.classList.remove('show');
    cartContainer.classList.add('hide');
    isCartVisible = false;
  }
}

// font-family: 'Alegreya', serif;
// font-family: 'Alice', serif;
// font-family: 'Arapey', serif;
// font-family: 'Aref Ruqaa', serif;
// font-family: 'Cantata One', serif;
// font-family: 'Domine', serif;
// font-family: 'Droid Serif', serif;
// font-family: 'Gentium Basic', serif;
// font-family: 'Libre Baskerville', serif;
// font-family: 'Lora', serif;
// font-family: 'Merriweather', serif;
// font-family: 'Old Standard TT', serif;
// font-family: 'Oranienbaum', serif;
// font-family: 'Prata', serif;
// font-family: 'Rufina', serif;
// font-family: 'Vidaloka', serif;
// font-family: 'Bentham', serif;
// font-family: 'Saira Extra Condensed', sans-serif;
// font-family: 'Saira', sans-serif;
// font-family: 'Lato', sans-serif;
// font-family: 'Open Sans', sans-serif;
// font-family: 'Oswald', sans-serif;
// font-family: 'Saira Condensed', sans-serif;
// font-family: 'Titillium Web', sans-serif;
// font-family: 'Quicksand', sans-serif;
// font-family: 'Nunito', sans-serif;
// font-family: 'Abel', sans-serif;
// font-family: 'Ruluko', sans-serif;
// font-family: 'Rum Raisin', sans-serif;
// font-family: 'Snippet', sans-serif;
// font-family: 'Chathura', sans-serif;
// font-family: 'Text Me One', sans-serif;
// font-family: 'Sansita', sans-serif;
// font-family: 'Wire One', sans-serif;
// font-family: 'Marvel', sans-serif;
// font-family: 'Bubbler One', sans-serif;
// font-family: 'Advent Pro', sans-serif;
// font-family: 'Amaranth', sans-serif;
// font-family: 'Convergence', sans-serif;

$(document).ready(function() {
  $.ajaxSetup({
    headers: {
        'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
    }
  });
  
  $('#id_region').change(function() {
      var regionId = $(this).val();
      var municipalitySelect = $('#id_municipality');
      // Limpiar las opciones anteriores
      municipalitySelect.empty();
      municipalitySelect.append('<option value="">Seleccione una comuna</option>');
      if (regionId) {
          $.ajax({
              url: "/api/municipalities/",
              data: { 'region_id': regionId },
              success: function(data) {
                  $.each(data, function(index, municipality) {
                      municipalitySelect.append('<option value="' + municipality.id + '">' + municipality.name + '</option>');
                  });
              },
              error: function(xhr, status, error) {
                  console.error("Error en la solicitud AJAX:", error);
              }
          });
      }
  });
});
